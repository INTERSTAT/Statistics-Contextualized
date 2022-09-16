from prefect import task, Flow, Parameter
from prefect.engine.state import Failed, Success
from requests import get, post, delete
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
from rdflib import Graph, Literal, URIRef, Namespace  # Basic RDF handling
from rdflib.namespace import RDF, RDFS, XSD, QB  # Most common namespaces
import pysftp
import json

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

# Fns ----


def raw_french_to_standard(df, age_classes, nuts3):
    """Transform the French census data source to our standard format.

    Arguments:
        df {dataframe} -- data source
        age_classes {list} -- a vector holding the age classes
    """
    # Adding an age class column
    ages_vector = df['AGED100']
    *age_classes_not_100, _ = age_classes
    age_groups = pd.cut(ages_vector, 20, labels=age_classes_not_100, right=False)
    df['AGE_CLASS'] = age_groups
    df['AGE_CLASS'] = df['AGE_CLASS'].cat.add_categories(['Y_GE100'])
    df.loc[df['AGED100'] == 100, 'AGE_CLASS'] = 'Y_GE100'

    # Grouping by age class
    df = df.groupby(by=['CODGEO', 'SEXE', 'AGE_CLASS'])['NB'].sum().reset_index()

    # Adding NUTS3
    df['CODGEO_COURT'] = df.apply(lambda row: row.CODGEO[0:3] if row.CODGEO[0:2] == '97' else row.CODGEO[0:2], axis=1) # FIXME column-wise

    df_with_nuts = df.merge(nuts3, left_on='CODGEO_COURT', right_on='departement')

    df_selected_cols = df_with_nuts[['CODGEO', 'nuts3', 'SEXE', 'AGE_CLASS', 'NB']]

    df_final = df_selected_cols.rename(columns={'CODGEO': 'lau', 'SEXE': 'sex', 'AGE_CLASS': 'age', 'NB': 'population'})

    return df_final


def raw_italian_to_standard(df, age_classes, nuts3):
    # Hold the variables of interest
    df_reduced = df[['ITTER107', 'SEXISTAT1', 'ETA1', 'Value']]

    # SEXISTAT1 & ETA1 variables includes subtotal, we only have to keep ventilated data
    df_filtered = df_reduced.loc[~((df_reduced['SEXISTAT1'] == 'T') | (df_reduced['ETA1'] == 'TOTAL') | (df_reduced['ITTER107'].str.strip().str[0:2] == 'IT'))]

    # Age & sex range have to be recoded to be mapped with the reference code list
    df_filtered['ETA1'] = df_filtered['ETA1'].replace('Y_UN4', 'Y_LT5')
    df_filtered['SEXISTAT1'] = df_filtered.apply(lambda row: "1" if row.SEXISTAT1 == 'M' else '2', axis=1)

    df_final = df_filtered.rename(columns={'ITTER107': 'lau', 'SEXISTAT1': 'sex', 'ETA1': 'age', 'Value': 'population'})

    df_with_nuts = df_final.merge(nuts3, left_on='lau', right_on='lau')

    return df_with_nuts

# Tasks ----


@task(name='Import DSD')
def import_dsd():
    g = Graph()
    g.parse("https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/pilots/sep/sep-dsd-1.ttl", format="turtle")
    return g.serialize(format="turtle", encoding='utf-8')

@task(name='Import TTL')
def import_ttl(url):
    g = Graph()
    g.parse(url, format="turtle")
    return g.serialize(format="turtle", encoding='utf-8')

@task(name='Retrieve age groups')
def get_age_class_data(url):
    resp = get(url)
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return list(df['group'])


@task(name='Retrieve French NUTS3')
def get_nuts3_fr(url):
    resp = get(url)
    data = BytesIO(resp.content)
    df = pd.read_csv(data)   
    return df


@task(name='Retrieve French Census data')
def extract_french_census(url, age_classes, nuts3):
    resp = get(url)
    archive = ZipFile(BytesIO(resp.content))
    file_in_zip = archive.namelist().pop()
    df = pd.read_csv(archive.open(file_in_zip), sep=';', dtype="string")
    df["NB"] = df["NB"].astype("float64")
    df["AGED100"] = df["AGED100"].astype("int")
    standard_df = raw_french_to_standard(df, age_classes, nuts3)
    return standard_df


@task(name='Retrieve Italian NUTS3')
def get_nuts3_it(url):
    resp = get(url)
    archive = ZipFile(BytesIO(resp.content))
    file_in_zip = archive.namelist().pop()
    df = pd.read_csv(archive.open(file_in_zip), sep=';', dtype="string")
    df_selected_cols = df[['LAU', 'NUTS3']]
    df_renamed = df_selected_cols.rename(columns={'LAU': 'lau', 'NUTS3': 'nuts3'})
    return df_renamed


@task(name='Retrieve Italian Census data')
def extract_italian_census(url, age_classes, nuts3):
    resp = get(url)
    archive = ZipFile(BytesIO(resp.content))
    file_in_zip = archive.namelist().pop()
    df = pd.read_csv(archive.open(file_in_zip), sep=',', dtype="string")
    standard_df = raw_italian_to_standard(df, age_classes, nuts3)
    return standard_df


@task(name='Concatenate data frames')
def concat_datasets(ds1, ds2):
    return pd.concat([ds1, ds2])


@task(name='Create RDF data')
def build_rdf_data(df):
    g = Graph()
    files = []
    SDMX_CONCEPT = Namespace('http://purl.org/linked-data/sdmx/2009/concept#')
    SDMX_ATTRIBUTE = Namespace('http://purl.org/linked-data/sdmx/2009/attribute#')
    SDMX_MEASURE = Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
    ISC = Namespace('http://id.cef-interstat.eu/sc/')

    # Generate prefixes
    g.bind('qb', QB)
    g.bind('sdmx_concept', SDMX_CONCEPT)
    g.bind('sdmx_attribute', SDMX_ATTRIBUTE)
    g.bind('sdmx_measure', SDMX_MEASURE)
    g.bind('isc', ISC)

    # Create DS
    dsURI = ISC.ds1
    g.add((dsURI, RDF.type, QB.DataSet))
    g.add((dsURI, QB.structure, ISC.dsd1))
    g.add((dsURI, RDFS.label, Literal('Population 15 and over by sex, age and activity status', lang='en')))
    g.add((dsURI, RDFS.label, Literal("Population de 15 ans ou plus par sexe, âge et type d'activité", lang='fr')))
    g.add((dsURI, SDMX_ATTRIBUTE.unitMeasure, URIRef('urn:sdmx:org.sdmx.infomodel.codelist.Code=ESTAT:CL_UNIT(1.2).PS')))

    dimAgeURI = URIRef(ISC + 'dim-age')
    dimSexURI = URIRef(ISC + 'dim-sex')
    dimLauURI = URIRef(ISC + 'dim-lau')
    attNutsURI = URIRef(ISC + 'att-nuts3')

    # Create observations
    for index, row in df.iterrows():
        sex = row['sex']
        sexURI = URIRef(ISC + 'sex-' + sex)
        age = row['age']
        ageURI = URIRef(ISC + 'age-' + age)
        lau = row['lau']
        lauURI = URIRef(ISC + 'lau-' + lau)
        nuts3 = row['nuts3']
        nuts3URI = URIRef(ISC + 'nuts3-' + nuts3)
        population = Literal(row['population'], datatype = XSD.float)

        obsURI = URIRef(ISC + 'obs-' + age + '-' + sex + '-' + lau)

        g.add((obsURI, RDF.type, QB.Observation))
        g.add((obsURI, QB.dataSet, ISC.ds1))
        g.add((obsURI, dimAgeURI, ageURI))
        g.add((obsURI, dimSexURI, sexURI))
        g.add((obsURI, dimLauURI, lauURI))
        g.add((obsURI, attNutsURI, nuts3URI))
        g.add((obsURI, SDMX_MEASURE.obsValue, population))

        if index % 200000 == 0 or index == len(df):
            file = g.serialize(format='turtle', encoding='utf-8')
            files.append(file)
            g = Graph()
    return files


@task(name='Delete RDF graph')
def delete_graph(url):
    res_delete = delete(url)

    if res_delete.status_code != 204:
        return Failed(f"Delete graph failed: {str(res_delete.status_code)}")
    else: 
        return Success("Graph deleted")


@task(name='Load RDF graph in triple store')
def load_turtle(ttl, url):
    headers = {'Content-Type': 'text/turtle'}
    
    res_post = post(url, data=ttl, headers=headers)

    if res_post.status_code != 204:
        return Failed(f"Post graph failed: {str(res_post.status_code)}")
    else:
        return Success(f"Graph loaded")


@task(name='Load list of RDF files in triple store')
def load_turtles(ttl_list, url):
    headers = {'Content-Type': 'text/turtle'}

    for f in ttl_list:
        res_post = post(url, data=f, headers=headers)


@task(name='Load file to FTP server')
def write_csv_on_ftp(df):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  

    # TODO: Use temporary file
    csv = df.to_csv(r'census_fr_it.csv', index=False, header=True)

    with open("./code/Python/secrets.json") as sf:
        secrets = json.load(sf)
        FTP_URL = secrets["ftp"]["url"]
        FTP_USER = secrets["ftp"]["user"]
        FTP_PASSWORD = secrets["ftp"]["password"]
    with pysftp.Connection(FTP_URL, username=FTP_USER, password=FTP_PASSWORD, cnopts=cnopts) as sftp:
        with sftp.cd('files/sep/output/'):
            sftp.put('census_fr_it.csv')
    

with Flow('census_csv_to_rdf') as flow:

    with open("./code/Python/secrets.json") as sf:
        secrets = json.load(sf)
        GRAPHDB_URL = secrets["graphdb"]["url"]

    sep_repository = 'sep-staging'
    metadata_graph_url = 'http://rdf.interstat.eng.it/graphs/sep/metadata'
    data_graph_url = 'http://rdf.interstat.eng.it/graphs/sep'

    metadata_rdf_repo_url = Parameter('metadata_rdf_repo_url', default=GRAPHDB_URL + "repositories/" + sep_repository + "/statements?context=<" + metadata_graph_url + ">")
    data_rdf_repo_url = Parameter('data_rdf_repo_url', default=GRAPHDB_URL + "repositories/" + sep_repository + "/statements?context=<" + data_graph_url + ">")

    delete_graph(metadata_rdf_repo_url)
    delete_graph(data_rdf_repo_url)

    dsd_rdf = import_dsd()
    load_turtle(dsd_rdf, metadata_rdf_repo_url)

    # START: Produced externally
    lau_fr_2020_data_url = Parameter('lau_fr_2020_data_url', default='https://interstat.eng.it/files/sep/input/lau-fr-2020.ttl')
    lau_fr_2020_rdf = import_ttl(lau_fr_2020_data_url)
    load_turtle(lau_fr_2020_rdf, metadata_rdf_repo_url)

    lau_it_2020_data_url = Parameter('lau_it_2020_data_url', default='https://interstat.eng.it/files/sep/input/lau-it-2020.ttl')
    lau_it_2020_rdf = import_ttl(lau_it_2020_data_url)
    load_turtle(lau_it_2020_rdf, metadata_rdf_repo_url)

    nuts3_2016_data_url = Parameter('nuts3_2016_data_url', default='https://interstat.eng.it/files/sep/input/nuts3-2016.ttl')
    nuts3_2016_rdf = import_ttl(nuts3_2016_data_url)
    load_turtle(nuts3_2016_rdf, metadata_rdf_repo_url)
    # END 

    age_class_url = Parameter('age_class_url', default="https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/pilots/resources/age-groups.csv")
    age_classes = get_age_class_data(age_class_url)
    
    nuts3_fr_url = Parameter('nuts3_fr_url', default='https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/pilots/resources/dep-nuts3-fr.csv')
    nuts3_fr = get_nuts3_fr(nuts3_fr_url)
    french_census_data_url = Parameter('fr_url', default='https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip')
    french_census = extract_french_census(french_census_data_url, age_classes, nuts3_fr)

    nuts3_it_url = Parameter('nuts3_it_url', default='https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/pilots/resources/nuts3_lau-it.zip')
    nuts3_it = get_nuts3_it(nuts3_it_url)
    italian_census_data_url = Parameter('it_url', default='https://interstat.eng.it/files/sep/input/census-it-2018.zip')
    italian_census = extract_italian_census(italian_census_data_url, age_classes, nuts3_it)
    
    df_fr_it = concat_datasets(french_census, italian_census)

    write_csv_on_ftp(df_fr_it)

    graph_files = build_rdf_data(df_fr_it)

    load_turtles(graph_files, data_rdf_repo_url)


def main():
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep')
    else:
        flow.run()

'''
This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep
'''
from prefect import task, Flow, Parameter
from prefect.engine.state import Failed, Success
from requests import get, post, delete
from zipfile import ZipFile
from io import BytesIO
from datetime import timedelta
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import RDF, RDFS, XSD, QB #most common namespaces
import urllib.parse #for parsing strings to URI's
import numpy as np

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

# Fns ----

def raw_french_to_standard(df, age_classes, nuts3):
    '''Transform the french census data source to our standard format.

    Arguments:
        df {dataframe} -- data source
        age_classes {list} -- a vector holding the age classes
    '''
    # Adding a age class column
    ages_vector = df['AGED100']
    *age_classes_not_100, _ = age_classes
    age_groups = pd.cut(ages_vector, 20, labels=age_classes_not_100, right=False)
    df['AGE_CLASS'] = age_groups
    df['AGE_CLASS'] = df['AGE_CLASS'].cat.add_categories(['Y_GE100'])
    df.loc[df['AGED100'] == 100, 'AGE_CLASS'] = 'Y_GE100'

    # Grouping by age class
    df = df.groupby(by=['CODGEO', 'SEXE','AGE_CLASS'])['NB'].sum().reset_index()

    # Adding NUTS3
    df['CODGEO_COURT'] = df.apply(lambda row: row.CODGEO[0:3] if row.CODGEO[0:2] == '97' else row.CODGEO[0:2], axis=1) # FIXME column-wise

    df_with_nuts = df.merge(nuts3, left_on='CODGEO_COURT', right_on='departement')

    df_selected_cols = df_with_nuts[['CODGEO', 'nuts3', 'SEXE', 'AGE_CLASS', 'NB']]

    df_final = df_selected_cols.rename(columns={'CODGEO': 'lau', 'SEXE': 'sex', 'AGE_CLASS': 'age', 'NB': 'population'})

    return df_final

def raw_italian_to_standard(df, age_classes):
    # Hold the variables of interest
    df_reduced = df[['ITTER107', 'SEXISTAT1', 'ETA1', 'Value', 'NUTS3']]

    # SEXISTAT1 & ETA1 variables includes subtotal, we only have to keep ventilated data
    df_filtered = df_reduced.loc[(df_reduced['SEXISTAT1'] != 'T') | (df_reduced['ETA1'] != 'TOTAL')]

    # Age range has to be recoded to be mapped with the reference code list
    df_filtered['ETA1'] = df_filtered.apply(lambda row: row.ETA1 if row.ETA1 == 'Y_UN4' else 'Y_LT5', axis=1)

    df_final = df_filtered.rename(columns={'ITTER107': 'lau', 'SEXISTAT1': 'sex', 'ETA1': 'age', 'Value': 'population', 'NUTS3': 'nuts3'})
    return df_final

# Tasks ----

@task
def import_dsd():
    g = Graph()
    g.parse("https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/sep-dsd-1.ttl", format="turtle")
    return g.serialize(format="turtle")

@task
def get_age_class_data():
    resp = get('https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/age-groups.csv')
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(list(df['group']))

@task
def get_nuts3():
    resp = get('https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/nuts3.csv')
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(df)

@task
def extract_french_census(url, age_classes, nuts3):
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip), sep=';', dtype="string")
    df["NB"] = df["NB"].astype("float64")
    df["AGED100"] = df["AGED100"].astype("int")
    standard_df = raw_french_to_standard(df, age_classes, nuts3)
    return standard_df

@task
def extract_italian_census(url, age_classes):
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip), sep=',', dtype="string")
    print(df)
    standard_df = raw_italian_to_standard(df, age_classes)
    return standard_df

@task
def concat_datasets(ds1, ds2):
    return pd.concat([ds1, ds2])

@task
def build_rdf_data(df):
    g = Graph()
    SDMX_CONCEPT = Namespace('http://purl.org/linked-data/sdmx/2009/concept#')
    SDMX_ATTRIBUTE = Namespace('http://purl.org/linked-data/sdmx/2009/attribute#')
    SDMX_MEASURE = Namespace('http://purl.org/linked-data/sdmx/2009/measure#')
    ISC = Namespace('http://id.cef-interstat.eu/sc/')

    # Generate prefixes
    g.bind('qb', QB)
    g.bind('sdmx_concept', SDMX_ATTRIBUTE)
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

    return g.serialize(format='turtle')

@task 
def delete_graph(url):
    res_delete = delete(url)

    if res_delete.status_code != 204:
        return Failed(f"Delete graph failed: {str(res_delete.status_code)}")
    else: 
        return Success(f"Graph deleted")

@task
def load_turtle(ttl, url):
    headers = {'Content-Type': 'text/turtle'}
    
    res_post = post(url, data=ttl, headers=headers)

    if res_post.status_code != 204:
        return Failed(f"Post graph failed: {str(res_post.status_code)}")
    else:
        return Success(f"Graph loaded")
    

with Flow('census_csv_to_rdf') as flow:

    repo_url = Parameter('repo_url', default="https://interstat.opsi-lab.it/graphdb/repositories/sep-test/statements?context=<http://www.interstat.org/graphs/sep>")

    delete_graph(repo_url)

    dsd_rdf = import_dsd()
    load_turtle(dsd_rdf, repo_url)

    age_classes = get_age_class_data()
    nuts3 = get_nuts3()

    french_census_data_url = Parameter('fr_url', default='https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip')
    french_census = extract_french_census(french_census_data_url, age_classes, nuts3)

    italian_census_data_url = Parameter('it_url', default='https://minio.lab.sspcloud.fr/l4tu7k/census-it.zip')
    italian_census = extract_italian_census(italian_census_data_url, age_classes)

    df = concat_datasets(french_census, italian_census)

    census_rdf = build_rdf_data(french_census)

    flow_status = load_turtle(census_rdf, repo_url)

if __name__ == '__main__':
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep')
    else:
        flow.run()
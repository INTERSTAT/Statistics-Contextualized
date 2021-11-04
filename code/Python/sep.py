"""
This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep
"""
from prefect import task, Flow, Parameter
from requests import get
from zipfile import ZipFile
from io import BytesIO
from datetime import timedelta
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import RDF, RDFS, XSD, QB #most common namespaces
import urllib.parse #for parsing strings to URI's

# Fns ----

def raw_french_to_standard(df, age_classes):
    v = df["AGED100"]
    *age_classes_not_100, _ = age_classes
    c = pd.cut(v, 20, labels=age_classes_not_100, right=False)
    df["AGE_CLASS"] = c
    df["AGE_CLASS"] = df["AGE_CLASS"].cat.add_categories(["Y_GE100"])
    print(df["AGE_CLASS"].cat.categories)
    df.loc[df["AGED100"] == 100, "AGE_CLASS"] = "Y_GE100" 
    print(df)

def raw_italian_to_standard(df):
    pass

# Tasks ----

@task(cache_for=timedelta(hours=1))
def get_age_class_data():
    resp = get("https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/age-groups.csv")
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(list(df["group"]))


@task(cache_for=timedelta(hours=1))
def extract_french_census(url, age_classes):
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip), sep=";")
    raw_french_to_standard(df, age_classes)
    return(df)

@task
def extract_italian_census(url):
    resp = get(url)
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(df)

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
    g.add((dsURI, RDFS.label, Literal("Population 15 and over by sex, age and activity status", lang="en")))
    g.add((dsURI, RDFS.label, Literal("Population de 15 ans ou plus par sexe, âge et type d'activité", lang="fr")))
    g.add((dsURI, SDMX_ATTRIBUTE.unitMeasure, URIRef("urn:sdmx:org.sdmx.infomodel.codelist.Code=ESTAT:CL_UNIT(1.2).PS")))

    dimAgeURI = URIRef(ISC + "dim-age")
    dimSexURI = URIRef(ISC + "dim-sex")
    dimLauURI = URIRef(ISC + "dim-lau")
    attNutsURI = URIRef(ISC + "att-nuts3")

    # Create observations
    for index, row in df.iterrows():
        sex = row['SEXISTAT1']
        sexURI = URIRef(ISC + "sex-" + sex)
        age = row['ETA1']
        ageURI = URIRef(ISC + "age-" + age)
        # lau = row['LAU']
        # lauURI = URIRef(ISC + "lau-" + lau)
        nuts3 = row['ITTER107']
        nuts3URI = URIRef(ISC + "nuts3-" + nuts3)
        population = Literal(row["Value"], datatype = XSD.float)

        obsURI = URIRef(ISC + "obs-" + age + "-" + sex + "-" + "lau")

        g.add((obsURI, RDF.type, QB.Observation))
        g.add((obsURI, QB.dataSet, ISC.ds1))
        g.add((obsURI, dimAgeURI, ageURI))
        g.add((obsURI, dimSexURI, sexURI))
        # g.add((obsURI, dimLauURI, lauURI))
        g.add((obsURI, attNutsURI, nuts3URI))
        g.add((obsURI, SDMX_MEASURE.obsValue, Literal("1")))

    print(g.serialize(format='turtle'))
    g.serialize(destination = 'census_rdf.ttl', format='turtle')

with Flow("census_csv_to_rdf") as flow:
    age_classes = default=get_age_class_data()

    french_census_data_url = Parameter("fr_url", default="https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip")
    french_census = extract_french_census(french_census_data_url, age_classes)
    
    # italian_census_data_url = Parameter("it_url", default="https://minio.lab.sspcloud.fr/l4tu7k/Census_IT_2018.csv")
    # italian_census = extract_italian_census(italian_census_data_url)

    # french_rdf_census = build_rdf_data(french_census)
    # italian_rdf_census = build_rdf_data(italian_census)
     

if __name__ == "__main__":
    flow.register(project_name="sep")
    flow.run()


"""
This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep
"""
from prefect import task, Flow
from requests import get
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import RDF, RDFS, XSD, QB #most common namespaces
import urllib.parse #for parsing strings to URI's

@task
def import_french_census():
    url = "https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip"
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip))
    print(df.head)
    return(df)

@task
def import_italian_census():
    url = "https://minio.lab.sspcloud.fr/l4tu7k/Census_IT_2018.csv"
    df = pd.read_csv(url)
    print(df.head)
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
        population = Literal(row["Value"], datatype = XSD.FLOAT)

        obsURI = URIRef(ISC + "obs-" + age + "-" + sex + "-" + "lau")

        g.add((obsURI, RDF.type, QB.Observation))
        g.add((obsURI, QB.dataSet, ISC.ds1))
        g.add((obsURI, dimAgeURI, ageURI))
        g.add((obsURI, dimSexURI, sexURI))
        # g.add((obsURI, dimLauURI, lauURI))
        g.add((obsURI, attNutsURI, nuts3URI))
        g.add((obsURI, SDMX_MEASURE.obsValue, Literal("1")))

    print(g.serialize(format='turtle'))
    g.serialize(destination = 'italian_census_rdf.ttl', format='turtle')

with Flow("sep") as flow:
    # french_census = import_french_census()
    italian_census = import_italian_census()
    italian_rdf_census = build_rdf_data(italian_census)

if __name__ == "__main__":
    flow.run()


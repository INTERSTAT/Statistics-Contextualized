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

@task
def extract_french_census(url):
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip))
    return(df)

@task
def extract_italian_census(url):
    resp = get(url)
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(df)

with Flow("sep") as flow:
    french_census_data_url = Parameter("fr_url", default="https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip")
    french_census = extract_french_census(french_census_data_url)

    italian_census_data_url = Parameter("it_url", default="https://minio.lab.sspcloud.fr/l4tu7k/Census_IT_2018.csv")
    extract_italian_census(italian_census_data_url)



if __name__ == "__main__":
    flow.run()


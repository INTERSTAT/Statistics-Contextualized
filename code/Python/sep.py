"""
This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep
"""
from prefect import task, Flow
from requests import get
from zipfile import ZipFile
from io import BytesIO
import pandas as pd

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
    pass

with Flow("sep") as flow:
    french_census = import_french_census()

if __name__ == "__main__":
    flow.run()


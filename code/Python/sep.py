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

with Flow("sep") as flow:
    age_classes = default=get_age_class_data()

    french_census_data_url = Parameter("fr_url", default="https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip")
    french_census = extract_french_census(french_census_data_url, age_classes)

    italian_census_data_url = Parameter("it_url", default="https://minio.lab.sspcloud.fr/l4tu7k/Census_IT_2018.csv")
    extract_italian_census(italian_census_data_url)

if __name__ == "__main__":
    # Overloading URL because Insee website is laggy
    flow.run(parameters=dict(fr_url="https://minio.lab.sspcloud.fr/l4tu7k/BTT_TD_POP1B_2018.zip"))


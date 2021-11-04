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
import numpy as np

# Fns ----

def raw_french_to_standard(df, age_classes, nuts3):
    """Transform the french census data source to our standard format.

    Arguments:
        df {dataframe} -- data source
        age_classes {list} -- a vector holding the age classes
    """
    # Adding a age class column
    ages_vector = df["AGED100"]
    *age_classes_not_100, _ = age_classes
    age_groups = pd.cut(ages_vector, 20, labels=age_classes_not_100, right=False)
    df["AGE_CLASS"] = age_groups
    df["AGE_CLASS"] = df["AGE_CLASS"].cat.add_categories(["Y_GE100"])
    df.loc[df["AGED100"] == 100, "AGE_CLASS"] = "Y_GE100"

    # Grouping by age class
    df = df.groupby(by=["CODGEO", "SEXE","AGE_CLASS"])["NB"].sum().reset_index()

    # Adding NUTS3
    df["CODGEO_COURT"] = df.apply(lambda row: row.CODGEO[0:3] if row.CODGEO[0:2] == "97" else row.CODGEO[0:2], axis=1) # FIXME column-wise

    df_with_nuts = df.merge(nuts3, left_on="CODGEO_COURT", right_on="departement")

    df_selected_cols = df_with_nuts[["CODGEO", "nuts3", "SEXE", "AGE_CLASS", "NB"]]

    df_final = df_selected_cols.rename(columns={"CODGEO": "lau", "SEXE": "sex", "AGE_CLASS": "age", "NB": "population"})

    print(df_final)

    return(df_final)

def raw_italian_to_standard(df):
    pass

# Tasks ----

@task
def get_age_class_data():
    resp = get("https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/age-groups.csv")
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(list(df["group"]))

@task
def get_nuts3():
    resp = get("https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/nuts3.csv")
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(df)

@task
def extract_french_census(url, age_classes, nuts3):
    resp = get(url)
    zip = ZipFile(BytesIO(resp.content))
    file_in_zip = zip.namelist().pop()
    df = pd.read_csv(zip.open(file_in_zip), sep=";")
    df["CODGEO"] = df["CODGEO"].astype("string")
    standard_df = raw_french_to_standard(df, age_classes, nuts3)
    return(standard_df)

@task
def extract_italian_census(url):
    resp = get(url)
    data = BytesIO(resp.content)
    df = pd.read_csv(data)
    return(df)

with Flow("sep") as flow:
    age_classes = get_age_class_data()

    nuts3 = get_nuts3()

    french_census_data_url = Parameter("fr_url", default="https://www.insee.fr/fr/statistiques/fichier/5395878/BTT_TD_POP1B_2018.zip")
    french_census = extract_french_census(french_census_data_url, age_classes, nuts3)

    italian_census_data_url = Parameter("it_url", default="https://minio.lab.sspcloud.fr/l4tu7k/Census_IT_2018.csv")
    extract_italian_census(italian_census_data_url)

if __name__ == "__main__":
    # Overloading URL because Insee website is laggy
    flow.run(parameters=dict(fr_url="https://minio.lab.sspcloud.fr/l4tu7k/BTT_TD_POP1B_2018.zip"))


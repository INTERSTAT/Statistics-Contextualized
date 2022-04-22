"""
This module is dedicated to API calls.
"""
import gzip
import pandas as pd
from urllib.parse import quote
from requests import get, post, delete, codes
from prefect.engine import signals


def get_french_schools_data() -> pd.DataFrame:
    """
    Calling the french schools data API.

    TODO expose API parameters as function params
    """
    base_url = "https://data.education.gouv.fr/api/v2/catalog/datasets"
    dataset_id = (
        "fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre"
    )
    row_limit = -1  # -1 means no limit
    filter_school_state = 1
    # TODO create two lists and join'em around 'AS' ?
    cols = [
        "numero_uai AS school_id",
        "appellation_officielle AS name",
        "latitude",
        "longitude",
        "code_commune AS lau",
        "secteur_public_prive_libe AS institution_type",
        "nature_uai AS code_nature",
    ]
    cols_request = quote(",".join(cols))
    target = (
        f"{base_url}/{dataset_id}/exports/csv?select={cols_request}&limit={str(row_limit)}&refine"
        f".etat_etablissement={filter_school_state}&offset=0&timezone=UTC "
    )
    print(target)
    df = pd.read_csv(target, sep=";")
    return df


def get_italian_cultural_data(target_url: str) -> pd.DataFrame:
    # Getting data
    resp = get(target_url)

    if resp.status_code != codes.ok:
        raise Exception(
            f"Fail to connect to italian museums endpoint (status code: {str(resp.status_code)})"
        )

    raw_data = resp.json()

    # Building columns vectors
    table_generator = {key: [] for key in raw_data["head"]["vars"]}

    for result in raw_data["results"]["bindings"]:
        for variable in table_generator.keys():
            if variable in result.keys():
                table_generator[variable].append(result[variable]["value"])
            else:
                # handling potential missing values in source data
                table_generator[variable].append(None)

    # Creating the data frame from the table generator dict
    df = pd.DataFrame(table_generator)  # create index ?
    return df


def load_turtle(url: str, ttl_data: str, compression=False):
    """
    Upload a new RDF graph.

    FIXME the GraphDB API we are using does not support application/gzip or application/zip as MIME Types
    """
    # Before loading a new graph, we get rid of the previous one
    delete(url)

    ttl_final_data = None

    # Compress data
    if compression:
        print("Using compression")
        ttl_final_data = gzip.compress(bytes(ttl_data, "utf-8"))
        headers = {"Content-Type": "application/gzip"}
    else:
        ttl_final_data = ttl_data
        headers = {"Content-Type": "text/turtle"}
    
    print("Target URL :")
    print(f"  {url}")

    resp = post(url, data=ttl_final_data, headers=headers)
    
    if resp.status_code != 204:
        raise Exception(
            f"Error connecting to back-end, status code is: {resp.status_code} - {resp.text}"
        )
    return resp.status_code

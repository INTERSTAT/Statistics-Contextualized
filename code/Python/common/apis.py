"""
This module is dedicated to API calls.
"""
import pandas as pd
from urllib.parse import quote

def get_french_schools_data() -> pd.DataFrame:
    """
    Calling the french schools data API.

    TODO expose API parameters as function params
    """
    base_url = "https://data.education.gouv.fr/api/v2/catalog/datasets"
    dataset_id = "fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre"
    row_limit = 5
    filter_school_state = 1
    # TODO create two lists and join'em around 'AS' ?
    cols = ["numero_uai AS school_id", "appellation_officielle AS name", "latitude", "longitude", "code_commune AS lau", "secteur_public_prive_libe AS institution_type"]
    cols_request = quote(",".join(cols))
    target = f"{base_url}/{dataset_id}/exports/csv?select={cols_request}&limit={str(row_limit)}&refine.etat_etablissement={filter_school_state}&offset=0&timezone=UTC"
    df = pd.read_csv(target)
    return df
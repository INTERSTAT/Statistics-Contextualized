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
    dataset_id = "fr-en-ecoles-effectifs-nb_classes" 
    row_limit = 5
    # TODO create two lists and join'em around 'AS' ?
    cols = ["numero_ecole AS school_id", "denomination_principale AS name", "code_postal AS zip_code", "secteur AS institution_type"]
    cols_request = quote(",".join(cols))
    target = f"{base_url}/{dataset_id}/exports/csv?select={cols_request}&limit={str(row_limit)}&offset=0&timezone=UTC"
    df = pd.read_csv(target)
    return df
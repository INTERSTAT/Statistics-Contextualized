"""
This module is dedicated to API calls.
"""
import pandas as pd

def get_french_schools_data() -> pd.DataFrame:
    """
    Calling the french schools data API.

    TODO expose API parameters as function params
    """
    base_url = "https://data.education.gouv.fr/api/v2/catalog/datasets"
    dataset_id = "fr-en-ecoles-effectifs-nb_classes" 
    row_limit = 5
    cols = ["numero_ecole", "denomination_principale"]
    cols_request = "%2C%20".join(cols)
    target = f"{base_url}/{dataset_id}/exports/csv?select={cols_request}&limit={str(row_limit)}&offset=0&timezone=UTC"
    df = pd.read_csv(target)
    return df
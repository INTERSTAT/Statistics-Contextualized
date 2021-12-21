import requests
import pandas as pd
from prefect import task, Flow, Parameter
from zipfile import ZipFile
from io import BytesIO

# Constants
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

@task
def extract_french_data(url, types): # types = List and intended types of selected variables
    archive = ZipFile(BytesIO(requests.get(url).content))
    data_zip = [name for name in archive.namelist() if not name.startswith("varmod")][0]
    bpe_data = pd.read_csv(archive.open(data_zip), sep=";", usecols=types.keys()) # 'dtype = types' not used here because of 'NA' values
    return bpe_data

# Build flow
def build_flow():
    with Flow("GF-EF") as flow:
        bpe_zip_url = Parameter(name="bpe_zip_url", required=True)
        types = Parameter(name="types", required = False)
        french_data = extract_french_data(bpe_zip_url, types)
    return flow

# Run flow
if __name__ == "__main__":
    flow = build_flow()
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name="sample")
    else:
        flow.run(parameters={
            "bpe_zip_url": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip", "types": {"AN": str, "COUVERT": str, "DEPCOM": str, "ECLAIRE": str, "LAMBERT_X": float, "LAMBERT_Y": float, "NBSALLES": int, "QUALITE_XY": str, "TYPEQU": str}})
    # flow.visualize()






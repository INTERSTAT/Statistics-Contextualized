import requests
import pandas as pd
from prefect import task, Flow, Parameter
from zipfile import ZipFile
from io import BytesIO
import pysftp
import json

# Constants
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False
FTP_HOST = 'FTP_HOST'
FTP_USERNAME = 'FTP_USERNAME'
FTP_PASSWORD = 'FTP_PASSWORD'

types_var_mod = {"COD_VAR": str, "LIB_VAR": str, "COD_MOD": str, "LIB_MOD": str, "TYPE_VAR": str, "LONG_VAR": int}
CSVW_INTRO = {"@context": "http://www.w3.org/ns/csvw", "dc:title": "Équipements géolocalisés en 2020 : lieux "
                                                                   "d’exposition et patrimoine & enseignement",
              "dc:description": "Données de la base permanente des équipements (BPE)",
              "dc:creator": "Interstat", "tables": list()}
DATA_FILE_NAME = "gf_data_fr.csv"


@task
def extract_french_data(url, types={}, facilities_filter=()):
    """
    Extracts the French data about geolocalized facilities.

    Parameters
    ----------
    url : str
        URL of the data file
    types : dict
        List of names and intended data types of the variables to select
    facilities_filter : list
        List of types of facilities selected

    Returns
    -------
    DataFrame
        The data extracted
    """

    archive = ZipFile(BytesIO(requests.get(url).content))
    data_zip = [name for name in archive.namelist() if not name.startswith("varmod")][0]
    # if types is not specified, take all the variables
    if not types:
        bpe_data = pd.read_csv(archive.open(data_zip), sep=";")
    else:
        bpe_data = pd.read_csv(archive.open(data_zip), sep=";", dtype=types, usecols=types.keys())
    bpe_data["QUALITE_XY"] = bpe_data["QUALITE_XY"].map({"Acceptable": "0",
                                                         "Bonne": "1",
                                                         "Mauvaise": "2",
                                                         "Non géolocalisé": "3"},
                                                        na_action="ignore")
    # if facilities_filter is not empty, select only type of facilities starting with list of facility types
    if facilities_filter:
        bpe_data_filtered = bpe_data.loc[(bpe_data["TYPEQU"].str.startswith(facilities_filter))]
        return bpe_data_filtered
    return bpe_data


@task
def extract_french_metadata(url, types={}, facilities_filter=()):
    """
    Extracts the French metadata about geolocalized facilities.

    Parameters
    ----------
    url : str
        URL of the metadata file
    types : dict
        List of names and intended data types of the variables to select
    facilities_filter : tuple
        List of types of facilities selected

    Returns
    -------
    DataFrame
        The metadata extracted
    """
    archive = ZipFile(BytesIO(requests.get(url).content))
    metadata_zip = [name for name in archive.namelist() if name.startswith("varmod")][0]
    bpe_metadata = pd.read_csv(archive.open(metadata_zip), sep=";", usecols=types_var_mod.keys())
    if types:
        bpe_metadata = bpe_metadata.loc[bpe_metadata["COD_VAR"].isin(types)]
    if facilities_filter:
        indexes = bpe_metadata[(bpe_metadata["COD_VAR"] == "TYPEQU") & ~(bpe_metadata["COD_MOD"].isin(facilities_filter))].index
        bpe_metadata = bpe_metadata.drop(indexes)
    return bpe_metadata


@task
def get_typ_equ(bpe_metadata):
    typ_equ = bpe_metadata.loc[(bpe_metadata["COD_VAR"] == "TYPEQU"), ["COD_MOD", "LIB_MOD"]]
    return typ_equ


@task
def concat_datasets(ds1, ds2):
    return pd.concat([ds1, ds2], ignore_index=True).drop_duplicates()


def get_json_datatype(var_type):
    json_datatype = ""
    if var_type == "DECIMAL":
        json_datatype = "float"
    elif var_type == "ENTIER":
        json_datatype = "integer"
    elif var_type == "ANNEE":
        json_datatype = "gYear"
    return json_datatype


@task
def transform_metadata_to_csvw(bpe_metadata):
    """
    Transforms the French metadata to CSVW description.

    Parameters
    ----------
    bpe_metadata : Dataframe
        The metadata extracted

    Returns
    -------
    Dictionary
        Dictionary representing CSVW description
    """
    # Filter for selecting unique variables
    columns = bpe_metadata.loc[:, ["COD_VAR", "LIB_VAR", "TYPE_VAR"]].drop_duplicates(
        subset=["COD_VAR", "LIB_VAR", "TYPE_VAR"], ignore_index=True)
    csvw = CSVW_INTRO
    # Create dictionary for describing data file structure
    table_data = {"url": DATA_FILE_NAME, "tableSchema": {}}
    table_data["tableSchema"]["columns"] = []
    table_data["tableSchema"]["foreignKeys"] = []
    # Browse all variables
    for i in columns.index:
        cod_var = columns["COD_VAR"][i]
        lib_var = columns["LIB_VAR"][i]
        typ_var = columns["TYPE_VAR"][i]
        json_datatype = get_json_datatype(typ_var)
        column = {"titles": cod_var,
                  "dc:description": lib_var}
        if json_datatype:
            column["datatype"] = json_datatype
        # Variable type == "CHAR" means an external table (csv file) contains valid code lists
        if typ_var == "CHAR":
            column["name"] = cod_var + "_CODE"
            foreign_key = {"columReference": cod_var + "_CODE",
                           "reference": {"resource": cod_var,
                                         "columnReference": cod_var + "_CODE"}}
            table_data["tableSchema"]["foreignKeys"].append(foreign_key)
            # Describe external table containing valid code lists
            table_metadata = {"url": cod_var + ".csv", "tableSchema": {"columns": [
                {"name": cod_var + "_CODE", "titles": cod_var,
                 "dc:description": lib_var + " (code)"},
                {"titles": cod_var + "_LABEL", "dc:description": lib_var + " (label)"}]}}
            # Add external table description to CSVW
            csvw["tables"].append(table_metadata)
        # Add column description to table data description
        table_data["tableSchema"]["columns"].append(column)
    # Add table data description to CSVW description after loop
    csvw["tables"][0].update(table_data)
    return csvw


def write_file_on_ftp(file_source, target_directory):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # Commented lines while waiting for details on the FTP connection
    # with pysftp.Connection(FTP_HOST, username=FTP_USERNAME, password=FTP_PASSWORD, cnopts=cnopts) as sftp:
    # with sftp.cd(target_directory):
    # sftp.put(file_source)


@task
def write_csv_on_ftp(df):
    # TODO: Use temporary file
    csv = df.to_csv(DATA_FILE_NAME, index=False, header=True)
    write_file_on_ftp(DATA_FILE_NAME, 'files/gf/output/')


@task
def write_json_on_ftp(csvw):
    # TODO: Use temporary file
    json_file_name = DATA_FILE_NAME + "-metadata.json"
    with open(json_file_name, 'w', encoding="utf-8") as csvw_file:
        json.dump(csvw, csvw_file, ensure_ascii=False, indent=4)
    write_file_on_ftp(json_file_name, "files/gf/output")


# Build flow
def build_flow():
    with Flow("GF-EF") as flow:
        bpe_zip_url1 = Parameter(name="bpe_zip_url1", required=True)
        types1 = Parameter(name="types1", required=False)
        facilities_filter = Parameter(name="facilities_filter", required=False)
        french_data1 = extract_french_data(bpe_zip_url1, types1, facilities_filter)
        bpe_zip_url2 = Parameter(name="bpe_zip_url2", required=True)
        types2 = Parameter(name="types2", required=False)
        french_data2 = extract_french_data(bpe_zip_url2, types2)
        french_data = concat_datasets(french_data1, french_data2)
        write_csv_on_ftp(french_data)
        french_metadata1 = extract_french_metadata(bpe_zip_url1, types1, facilities_filter)
        french_metadata2 = extract_french_metadata(bpe_zip_url2, types2)
        french_metadata = concat_datasets(french_metadata1, french_metadata2)
        csvw = transform_metadata_to_csvw(french_metadata)
        write_json_on_ftp(csvw)
    return flow


# Run flow
if __name__ == "__main__":
    flow = build_flow()
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name="sample")
    else:
        flow.run(parameters={
            "bpe_zip_url1": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip",
            "types1": {"AN": str, "COUVERT": str, "DEPCOM": str, "ECLAIRE": str, "LAMBERT_X": float, "LAMBERT_Y": float,
                       "NBSALLES": "Int64", "QUALITE_XY": str, "TYPEQU": str},
            "facilities_filter": ("F309",),
            "bpe_zip_url2": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_enseignement_xy_csv.zip",
            "types2": {"AN": str, "CL_PELEM": str, "CL_PGE": str, "DEPCOM": str, "EP": str, "LAMBERT_X": float,
                       "LAMBERT_Y": float, "QUALITE_XY": str, "SECT": str, "TYPEQU": str}
        })
    flow.visualize()

import re
from unicodedata import name
import requests
import pandas as pd
from prefect import task, Flow, Parameter
from zipfile import ZipFile
from io import BytesIO
import pysftp
import json
import csv
import pathlib
import os

# Constants ----

# FTP config placeholders
FTP_URL = None
FTP_USER = None
FTP_PASSWORD = None

types_var_mod = {
    "COD_VAR": str,
    "LIB_VAR": str,
    "COD_MOD": str,
    "LIB_MOD": str,
    "TYPE_VAR": str,
    "LONG_VAR": int,
}
CSVW_INTRO = {
    "@context": "http://www.w3.org/ns/csvw",
    "dc:title": "Équipements géolocalisés en 2020 : lieux "
    "d’exposition et patrimoine & enseignement",
    "dc:description": "Données de la base permanente des équipements (BPE)",
    "dc:creator": "Interstat",
    "tables": list(),
}

DATA_FILE_NAME = "gf_data_fr.csv"
WORK_DIRECTORY = "../../../work/"

def flow_parameters(conf):
    wd = get_working_directory(conf)
    return {                
                "working_dir": wd,
                "bpe_zip_url1": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip",
                "bpe_metadata_url1": wd + "bpe-cultural-places-variables.csv",
                "types1": {
                    "AN": str,
                    "COUVERT": str,
                    "DEPCOM": str,
                    "ECLAIRE": str,
                    "LAMBERT_X": float,
                    "LAMBERT_Y": float,
                    "NBSALLES": "Int64",
                    "QUALITE_XY": str,
                    "TYPEQU": str,
                },
                "facilities_filter": ("F309",),
                "bpe_zip_url2": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_enseignement_xy_csv.zip",
                "bpe_metadata_url2": wd + "bpe-education-variables.csv",
                "types2": {
                    "AN": str,
                    "CL_PELEM": str,
                    "CL_PGE": str,
                    "DEPCOM": str,
                    "EP": str,
                    "LAMBERT_X": float,
                    "LAMBERT_Y": float,
                    "QUALITE_XY": str,
                    "SECT": str,
                    "TYPEQU": str,
                },                
                "italian_educational_data_url": "https://interstat.eng.it/files/gf/input/it/MIUR_Schools_with_coordinates.csv"
            }

def test_flow_parameters():
    return {"italian_educational_data_url": "C:/Users/ARKN1Q/Documents/code/Statistics-Contextualized/work/MIUR Schools with coordinates_new.csv"}

def get_conf():
    """
    Grab this pipeline conf, handling various operating systems.
    """
    project_path = pathlib.Path(__file__).cwd()
    sep = "\\" if os.name == "nt" else "/"
    conf_path = sep.join([str(project_path), "code", "Python", "gf", "gf.conf.json"])
    with open(conf_path) as conf:
        return json.load(conf)


def get_working_directory(conf=None):
    """
    If there is a working dir in the conf file, returns it, else returns a default one.
    """
    if conf is None or conf["env"]["workingDirectory"] == "":        
        project_path = pathlib.Path(__file__).cwd()          
        wd = str(project_path) + "/work/"        
        os.makedirs(wd, exist_ok=True)
        return wd
    else:
        return conf["env"]["workingDirectory"]


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
        bpe_data = pd.read_csv(
            archive.open(data_zip), sep=";", dtype=types, usecols=types.keys()
        )
    bpe_data["QUALITE_XY"] = bpe_data["QUALITE_XY"].map(
        {"Acceptable": "0", "Bonne": "1", "Mauvaise": "2", "Non géolocalisé": "3"},
        na_action="ignore",
    )
    # if facilities_filter is not empty, select only type of facilities starting with list of facility types
    if facilities_filter:
        bpe_data_filtered = bpe_data.loc[
            (bpe_data["TYPEQU"].str.startswith(facilities_filter))
        ]
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
    bpe_metadata = pd.read_csv(url, sep=",", usecols=types_var_mod.keys())
    if types:
        bpe_metadata = bpe_metadata.loc[bpe_metadata["COD_VAR"].isin(types)]
    if facilities_filter:
        indexes = bpe_metadata[
            (bpe_metadata["COD_VAR"] == "TYPEQU")
            & ~(bpe_metadata["COD_MOD"].isin(facilities_filter))
        ].index
        bpe_metadata = bpe_metadata.drop(indexes)
    return bpe_metadata


@task
def extract_italian_educational_data(url: str) -> pd.DataFrame:
    italian_educ_data: pd.DataFrame = pd.read_csv(url, sep=",")
    return italian_educ_data


@task
def concat_datasets(ds1, ds2):
    return pd.concat([ds1, ds2], ignore_index=True).drop_duplicates()


@task
def transform_data_to_csv(df, working_dir):
    return df.to_csv(working_dir + DATA_FILE_NAME, index=False, header=True)


@task
def transform_metadata_to_csvw(bpe_metadata, working_dir):
    """
    Transforms the French metadata to CSVW description.

    Parameters
    ----------
    bpe_metadata : Dataframe
        The metadata extracted

    Returns
    -------
    File
        json file representing CSVW description
    """
    # Filter for selecting unique variables (= columns)
    columns = bpe_metadata.loc[:, ["COD_VAR", "LIB_VAR", "TYPE_VAR"]].drop_duplicates(
        subset=["COD_VAR", "LIB_VAR", "TYPE_VAR"], ignore_index=True
    )
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
        metadata_table_name = cod_var.lower() + ".csv"
        json_datatype = get_json_datatype(typ_var)
        column = {"titles": cod_var, "dc:description": lib_var}
        if json_datatype:
            column["datatype"] = json_datatype
        # Variable type == "CHAR" means an external table (csv file) contains valid code lists
        if typ_var == "CHAR":
            column["name"] = cod_var
            foreign_key = {
                "columReference": cod_var,
                "reference": {
                    "resource": metadata_table_name,
                    "columnReference": cod_var + "_CODE",
                },
            }
            table_data["tableSchema"]["foreignKeys"].append(foreign_key)
            # Describe external table containing valid code lists
            table_metadata = {
                "url": metadata_table_name,
                "tableSchema": {
                    "columns": [
                        {
                            "name": cod_var + "_CODE",
                            "titles": cod_var + "_CODE",
                            "dc:description": lib_var + " (code)",
                        },
                        {
                            "titles": cod_var + "_LABEL",
                            "dc:description": lib_var + " (label)",
                        },
                    ]
                },
            }
            # Add external table description to CSVW
            csvw["tables"].append(table_metadata)
        # Add column description to table data description
        table_data["tableSchema"]["columns"].append(column)
    # Insert description of data table data to CSVW description
    csvw["tables"].insert(0, table_data)
    json_file_name = working_dir + DATA_FILE_NAME + "-metadata.json"
    with open(json_file_name, "w", encoding="utf-8") as csvw_file:
        json.dump(csvw, csvw_file, ensure_ascii=False, indent=4)
    return csvw_file


@task
def transform_metadata_to_code_lists(bpe_metadata, working_dir):
    """
    Transforms the French metadata to code list csv files.

    Parameters
    ----------
    bpe_metadata : Dataframe
        The metadata extracted

    Returns
    -------
    List
        List of files created. Each item is a CSV file representing one code list
    """
    bpe_metadata_variables = bpe_metadata.loc[
        :, ["COD_VAR", "LIB_VAR", "TYPE_VAR"]
    ].drop_duplicates(ignore_index=True)
    dict_var_code_lists = {"variables": []}
    for i in bpe_metadata_variables.index:
        cod_var = bpe_metadata_variables["COD_VAR"][i]
        typ_var = bpe_metadata_variables["TYPE_VAR"][i]
        mod = []
        if typ_var == "CHAR":
            code_list = bpe_metadata.loc[
                bpe_metadata["COD_VAR"] == bpe_metadata_variables["COD_VAR"][i],
                ["COD_MOD", "LIB_MOD"],
            ]
            code_list.dropna(inplace=True)
            for j in code_list.index:
                cod_mod = code_list["COD_MOD"][j]
                lib_mod = code_list["LIB_MOD"][j]
                mod.append({"codMod": cod_mod, "libMod": lib_mod})
            dict_var_code_lists["variables"].append({"codVar": cod_var, "mod": mod})
    files = []
    for x in dict_var_code_lists.get("variables"):
        cod_var = x["codVar"]
        file_name = working_dir + x["codVar"].lower() + ".csv"
        header_list = {"codMod": cod_var + "_CODE", "libMod": cod_var + "_LABEL"}
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["codMod", "libMod"])
            writer.writerow(header_list)
            for y in x["mod"]:
                writer.writerow(y)
        files.append(file)
    return files


@task
def load_files_to_ftp(csvw, code_lists, working_dir):
    """
    Loads all files created to FTP

    Parameters
    ----------
    csvw : File
        csvw description file (json)
    code_lists : List
        code list files (csv)

    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    remote_path = "files/gf/output/"
    with open("../secrets.json") as sf:
        secrets = json.load(sf)
        FTP_URL = secrets["ftp"]["url"]
        FTP_USER = secrets["ftp"]["user"]
        FTP_PASSWORD = secrets["ftp"]["password"]
    with pysftp.Connection(
        FTP_URL, username=FTP_USER, password=FTP_PASSWORD, cnopts=cnopts
    ) as sftp:
        sftp.makedirs(remote_path)  # Create remote path if needed
        with sftp.cd(remote_path):
            sftp.put(working_dir + DATA_FILE_NAME)
            sftp.put(csvw.name)
            for f in code_lists:
                sftp.put(f.name)


# Build flow
def build_flow(conf):
    with Flow("GF-EF") as flow:
        # Flow parameters
        working_dir = Parameter(
            name="working_dir", default=get_working_directory(conf), required=True
        )
        bpe_zip_url1 = Parameter(name="bpe_zip_url1", required=True)
        bpe_metadata_url1 = Parameter(name="bpe_metadata_url1", required=True)
        types1 = Parameter(name="types1", required=False)
        facilities_filter = Parameter(name="facilities_filter", required=False)
        bpe_zip_url2 = Parameter(name="bpe_zip_url2", required=True)
        bpe_metadata_url2 = Parameter(name="bpe_metadata_url2", required=True)
        types2 = Parameter(name="types2", required=False)

        italian_educational_data_url = Parameter(name="italian_educational_data_url", required=True)

        # Flow tasks
        french_data1 = extract_french_data(bpe_zip_url1, types1, facilities_filter)
        french_data2 = extract_french_data(bpe_zip_url2, types2)
        french_data = concat_datasets(french_data1, french_data2)
        french_metadata1 = extract_french_metadata(
            bpe_metadata_url1, types1, facilities_filter
        )
        french_metadata2 = extract_french_metadata(bpe_metadata_url2, types2)
        french_metadata = concat_datasets(french_metadata1, french_metadata2)
        csvw = transform_metadata_to_csvw(french_metadata, working_dir)
        code_lists = transform_metadata_to_code_lists(french_metadata, working_dir)

        extract_italian_educational_data(italian_educational_data_url)

        load_files_to_ftp(
            csvw,
            code_lists,
            working_dir,
            upstream_tasks=[transform_data_to_csv(french_data, working_dir)],
        )

    return flow

def build_test_flow():
    with Flow("gf-test") as flow:
        italian_educational_data_url = Parameter(name="italian_educational_data_url", required=True)
        extract_italian_educational_data(italian_educational_data_url)
    return flow


# Run flow
if __name__ == "__main__":

    conf = get_conf()    

    if conf["flags"]["flow"]["testing"]:
        flow = build_test_flow()
        params = test_flow_parameters()
    else:
        flow = build_flow(conf)
        params = flow_parameters(conf)
    

    if conf["flags"]["prefect"]["pushToCloudDashboard"]:
        flow.register(project_name="sample")
    else:        
        flow.run(            
            parameters=params
        )

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

import re
import time

import numpy as np
import requests
import pandas as pd
from prefect import task, Flow, Parameter
import prefect
from zipfile import ZipFile
from io import BytesIO
import pysftp
import json
import csv
import pathlib
import os
import logging
from urllib.parse import quote
from gf.gf_conf import conf
from common.geo_base import convert_coordinates_fn
from common.apis import get_italian_cultural_data, load_turtle
from common.rdf import (
    gen_rdf_facility,
    gen_rdf_geometry,
    gen_rdf_quality,
    gen_rdf_french_facility,
)

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
            "DEPCOM": str,
            "LAMBERT_X": float,
            "LAMBERT_Y": float,
            "QUALITE_XY": str,
            "TYPEQU": str,
        },
        "rename1": {
            "AN": "Year",
            "DEPCOM": "LAU",
            "LAMBERT_X": "Coord_X",
            "LAMBERT_Y": "Coord_Y",
            "QUALITE_XY": "Quality_XY",
            "TYPEQU": "Facility_Type",
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
        "rename2": {
            "AN": "Year",
            "DEPCOM": "LAU",
            "LAMBERT_X": "Coord_X",
            "LAMBERT_Y": "Coord_Y",
            "QUALITE_XY": "Quality_XY",
            "SECT": "Sector",
            "TYPEQU": "Facility_Type",
            "CL_PELEM": "CL_PELEM",
            "EP": "EP",
            "CL_PGE": "CL_PGE",
        },
        "italian_educational_data_url": "https://dati.istruzione.it/opendata/opendata/catalogo/elements1/leaf/EDIANAGRAFESTA20181920180901.csv",
    }


def test_flow_parameters():
    return None


def get_conf():
    """
    Grab this pipeline conf, handling various operating systems.
    """
    logging.info("Getting GF conf")
    project_path = pathlib.Path(__file__).cwd()

    sep = "\\" if os.name == "nt" else "/"
    conf_path = sep.join([str(project_path), "code", "Python", "gf", "gf.conf.json"])
    logging.info(f"Project path is {str(project_path)}")
    logging.info(f"Conf file path is {str(conf_path)}")
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
def extract_french_data(url, types={}, facilities_filter=(), rename={}):
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
    rename  : dict
        Dictionary for renaming columns

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
    bpe_data.rename(columns=rename, inplace=True)
    bpe_data["Quality_XY"] = bpe_data["Quality_XY"].map(
        {
            "Acceptable": "ACCEPTABLE",
            "Bonne": "GOOD",
            "Mauvaise": "BAD",
            "Non géolocalisé": "NO_GEOLOCALIZED",
        },
        na_action="ignore",
    )
    # if facilities_filter is not empty, select only type of facilities starting with list of facility types
    if facilities_filter:
        bpe_data_filtered = bpe_data.loc[
            (bpe_data["Facility_Type"].str.startswith(facilities_filter))
        ]
        return bpe_data_filtered

    return bpe_data


@task
def extract_french_metadata(url, rename={}, facilities_filter=()):
    """
    Extracts the French metadata about geolocalized facilities.

    Parameters
    ----------
    url : str
        URL of the metadata file
    rename : dict
        List of values renamed
    facilities_filter : tuple
        List of types of facilities selected

    Returns
    -------
    DataFrame
        The metadata extracted
    """
    bpe_metadata = pd.read_csv(url, sep=",", usecols=types_var_mod.keys())
    if rename:
        bpe_metadata = bpe_metadata.loc[bpe_metadata["COD_VAR"].isin(rename.values())]
    if facilities_filter:
        indexes = bpe_metadata[
            (bpe_metadata["COD_VAR"] == "Facility_Type")
            & ~(bpe_metadata["COD_MOD"].isin(facilities_filter))
        ].index
        bpe_metadata = bpe_metadata.drop(indexes)
    return bpe_metadata


@task
def extract_italian_educational_data(url: str) -> pd.DataFrame:
    italian_educ_data: pd.DataFrame = pd.read_csv(url, sep=",")
    italian_educ_data.rename(columns={"CODICESCUOLA": "Facility_ID"}, inplace=True)
    # Extract the 2019 from 201819
    # see https://regex101.com/r/3S04We/1
    start_end = re.compile(r"([0-9]{2}?)[0-9]{2}([0-9]{2}?)")
    italian_educ_data["Year"] = [
        "".join(start_end.match(str(year)).group(1, 2))
        for year in italian_educ_data["ANNOSCOLASTICO"]
    ]
    return italian_educ_data


def add_coordinates_italian_educational_data(df) -> pd.DataFrame:
    df_sample = df.sample(n=conf["thresholds"]["italianEducationFacilitiesGeocoding"])  # Impact on duration, n x 1.5 seconds
    df_sample["Coord_X"] = 0.0
    df_sample["Coord_Y"] = 0.0
    for index, row in df_sample.iterrows():
        TipologiaIndirizzo = row["TIPOLOGIAINDIRIZZO"]
        DenominazioneIndirizzo = row["DENOMINAZIONEINDIRIZZO"]
        DescrizioneComune = row["DESCRIZIONECOMUNE"]
        NumeroCivico = row["NUMEROCIVICO"]
        # Incomplete names are not found by the server (for example "via G. SIANI" or "via G.Leopardi")
        # so only the surname is taken (for example "via SIANI" or "via Leopardi)
        if ("." in DenominazioneIndirizzo) and (" " in DenominazioneIndirizzo):
            splitted = DenominazioneIndirizzo.split(" ")
        else:
            splitted = DenominazioneIndirizzo.split(".")
        DenominazioneIndirizzo = splitted[len(splitted) - 1]
        # If a comma is present, only the first part of the address or house number is considered
        if "," in DenominazioneIndirizzo:
            DenominazioneIndirizzo = DenominazioneIndirizzo.split(",")[0]
        if "," in NumeroCivico:
            NumeroCivico = NumeroCivico.split(",")[0]
        apiService = "https://nominatim.openstreetmap.org/search?street="
        url = (
            quote(TipologiaIndirizzo.encode("utf-8"))
            + "%20"
            + quote(DenominazioneIndirizzo.encode("utf-8"))
            + "+&city="
            + quote(DescrizioneComune.encode("utf-8"))
            + "&format=json&limit=1"
        )
        NumeroCivico_is_a_digit = False
        address_found = False
        # It checks whether the house number is a numerical value
        if bool(re.search(re.compile("^\d+$"), NumeroCivico)):
            NumeroCivico_is_a_digit = True
            api = apiService + quote(NumeroCivico.encode("utf-8")) + "+" + url
        else:
            api = apiService + url
        r = requests.get(api)
        data = r.json()
        if len(data) > 0:
            address_found = True
        if address_found:
            df_sample.loc[index, "Coord_X"] = data[0]["lat"]
            df_sample.loc[index, "Coord_Y"] = data[0]["lon"]
        time.sleep(1.5)  # wait a bit before sending the next request
    return df_sample


@task
def transform_italian_educational_data(df):
    df_coordinates = add_coordinates_italian_educational_data(df)
    url = (
        get_working_directory() + "Codici-statistici-e-denominazioni-al-31_12_2020.xls"
    )
    df_cadastral_lau = pd.read_excel(
        url, dtype=str, usecols=[4, 19], names=["LAU", "CADASTRAL_CODE"]
    )
    df_merged = df_coordinates.merge(
        df_cadastral_lau, left_on="CODICECOMUNE", right_on="CADASTRAL_CODE", how="left"
    )
    df_merged["Facility_Type"] = "C"
    df_merged["Sector"] = np.nan
    df_merged["Quality_XY"] = "GOOD"
    df_merged_restriction = df_merged[
        [
            "Year",
            "Facility_ID",
            "Facility_Type",
            "Coord_X",
            "Coord_Y",
            "LAU",
            "Sector",
            "Quality_XY",
        ]
    ]
    return df_merged_restriction


@task
def concat_datasets(ds1, ds2, id_prefix=None):
    """
    Use pandas native function to concat two data frames, and generate ids
    if asked.
    """
    df = pd.concat([ds1, ds2], ignore_index=True).drop_duplicates()
    if id_prefix is not None:
        df["Facility_ID"] = [f"{id_prefix}{i}" for i in range(1, len(df) + 1)]
    return df

@task(name="Transform french coordinates")
def transform_french_coordinates(df):
    tdf = convert_coordinates_fn(df, "Coord_X", "Coord_Y", "epsg:2154", "epsg:4326")
    tdf.assign(
        Coord_X=df["coord"][0], 
        Coord_Y=df["coord"][1]
        )
    return tdf

@task
def concat_metadatasets(ds1, ds2):
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
def extract_italian_cultural_facilities():
    logger = prefect.context.get("logger")
    # Building the query
    query = conf["sparql"]["italianCulturalFacilities"]
    limit = conf["thresholds"]["italianCulturalFacilities"]
    query_with_limit = query + f"limit {limit}" if limit is not None else query
    quoted_query = quote(query_with_limit.strip())
    target_url = f"https://dati.beniculturali.it/sparql?default-graph-uri=&query={quoted_query}&format=application%2Fjson"
    # Requesting data
    df = get_italian_cultural_data(target_url)
    logger.info(f"{len(df)} italian cultural facilities grabbed.")
    df["Year"] = "2022"
    # For italian museums, the last part of `subject` uri is the id
    df["Facility_ID"] = [subject.split("/")[-1] for subject in df["subject"]]
    df["Facility_Type"] = "F3"
    df["LAU"] = np.nan
    df["Sector"] = np.nan
    df["Quality_XY"] = "GOOD"
    df.rename(columns={"Latitudine": "Coord_X", "Longitudine": "Coord_Y"}, inplace=True)
    final_df = df[
        [
            "Year",
            "Facility_ID",
            "Coord_X",
            "Coord_Y",
            "Facility_Type",
            "LAU",
            "Sector",
            "Quality_XY",
        ]
    ]
    return final_df


@task
def extract_italian_cultural_events():
    logger = prefect.context.get("logger")
    # FIXME duplicated code → apis module?
    query = conf["sparql"]["italianCulturalEvents"]
    limit = conf["thresholds"]["italianCulturalEvents"]
    query_with_limit = query + f"limit {limit}"
    quoted_query = quote(query_with_limit.strip())
    # FIXME character encoding (ex: "Attivit\u00E0 Didattica")
    # FIXME (query) LATITUDINE and LONGITUDINE are always empty
    target_url = f"https://dati.beniculturali.it/sparql?default-graph-uri=&query={quoted_query}&format=application%2Fjson"

    df = get_italian_cultural_data(target_url)
    logger.info(f"{len(df)} italian cultural events grabbed.")
    return df


@task(name="Create RDF data")
def build_rdf_data(df):

    logger = prefect.context.get("logger")
    logger.info("Building a RDF file from the input data frame.")

    if all(col in df.columns for col in ["CL_PGE", "CL_PELEM", "EP"]):
        logger.debug("Generating RDF for french education facilities")
        df["FACILITY_RDF"] = [
            gen_rdf_french_facility(id, equ_type, sector, lau, pge, pelem, ep)
            for (id, equ_type, sector, lau, pge, pelem, ep) in zip(
                df["Facility_ID"],
                df["Facility_Type"],
                df["Sector"],
                df["LAU"],
                df["CL_PGE"],
                df["CL_PELEM"],
                df["EP"],
            )
        ]
    else:
        df["FACILITY_RDF"] = [
            gen_rdf_facility(id, equ_type, sector, lau)
            for (id, equ_type, sector, lau) in zip(
                df["Facility_ID"], df["Facility_Type"], df["Sector"], df["LAU"]
            )
        ]

    df["GEOMETRY_RDF"] = [
        gen_rdf_geometry(id, x, y)
        for (id, x, y) in zip(df["Facility_ID"], df["Coord_X"], df["Coord_Y"])
    ]
    df["QUALITY_RDF"] = [
        gen_rdf_quality(id, quality)
        for (id, quality) in zip(df["Facility_ID"], df["Quality_XY"])
    ]

    # Producing RDF text for the turtle file
    namespaces = """
    @prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix geo:     <http://www.opengis.net/ont/geosparql#> .
    @prefix igf:     <http://rdf.insee.fr/def/interstat/gf#> .
    @prefix dc:      <http://purl.org/dc/elements/1.1/> .
    @prefix dcterms: <http://purl.org/dc/terms/> .
    @prefix oa:      <http://www.w3.org/ns/oa#> .
    @prefix dqv:     <http://www.w3.org/ns/dqv#> .
    """
    raw_facility_rdf = "\n".join(df["FACILITY_RDF"])
    raw_geometry_rdf = "\n".join(df["GEOMETRY_RDF"])
    raw_quality_rdf = "\n".join(df["QUALITY_RDF"])
    final_rdf = "\n".join(
        [namespaces, raw_facility_rdf, raw_geometry_rdf, raw_quality_rdf]
    )

    return final_rdf


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
    with open("./code/Python/secrets.json") as sf:
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


@task
def concat_rdf_data(french_rdf: str, it_rdf: str):
    return french_rdf + "\n" + it_rdf


@task(name="Upload RDF data")
def upload_rdf_data(rdf_data):
    logger = prefect.context.get("logger")
    # FIXME as a Prefect parameter ?
    repo = conf["graphdbRepositories"]["test"]
    graph_url = f'{repo}statements?context=<http://www.interstat.org/graphs/gf>'
    logger.info(f"Uploading RDF data to {graph_url}")
    load_turtle(graph_url, rdf_data)


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
        rename1 = Parameter(name="rename1", required=False)
        facilities_filter = Parameter(name="facilities_filter", required=False)
        bpe_zip_url2 = Parameter(name="bpe_zip_url2", required=True)
        bpe_metadata_url2 = Parameter(name="bpe_metadata_url2", required=True)
        types2 = Parameter(name="types2", required=False)
        rename2 = Parameter(name="rename2", required=False)
        italian_educational_data_url = Parameter(
            name="italian_educational_data_url", required=True
        )

        # Flow tasks
        french_data1 = extract_french_data(
            bpe_zip_url1, types1, facilities_filter, rename1
        )
        french_data2 = extract_french_data(bpe_zip_url2, types2, rename=rename2)
        french_data = concat_datasets(french_data1, french_data2, id_prefix="fr")

        # WIP - Transform Lambert to WGS84 
        #french_data = transform_french_coordinates(french_data)

        french_metadata1 = extract_french_metadata(
            bpe_metadata_url1, rename1, facilities_filter
        )
        french_metadata2 = extract_french_metadata(bpe_metadata_url2, rename2)
        french_metadata = concat_metadatasets(french_metadata1, french_metadata2)
        csvw = transform_metadata_to_csvw(french_metadata, working_dir)
        code_lists = transform_metadata_to_code_lists(french_metadata, working_dir)

        italian_educational_data = extract_italian_educational_data(
            italian_educational_data_url
        )

        italian_educational_data_transformed = transform_italian_educational_data(
            italian_educational_data
        )
        italian_cultural_facilities = extract_italian_cultural_facilities()
        # italian_cultural_events = extract_italian_cultural_events()

        italian_data = concat_datasets(
            italian_educational_data_transformed, italian_cultural_facilities
        )

        french_rdf_data = build_rdf_data(french_data)
        it_rdf_data = build_rdf_data(italian_data)
        rdf_data = concat_rdf_data(french_rdf_data, it_rdf_data)
        upload_rdf_data(rdf_data)

        """ This task doesn't work on some networks
        load_files_to_ftp(
            csvw,
            code_lists,
            working_dir,
            upstream_tasks=[transform_data_to_csv(french_data, working_dir)],
        )
        """

    return flow


def build_test_flow():
    with Flow("gf-test") as flow:
        data = extract_italian_educational_data(
            "https://dati.istruzione.it/opendata/opendata/catalogo/elements1/leaf/EDIANAGRAFESTA20181920180901.csv"
        )
        data_transformed = transform_italian_educational_data(data)
    return flow


def main():
    """
    Main entry point for the GF pipeline.
    """
    if conf["flags"]["flow"]["testing"]:
        flow = build_test_flow()
        params = test_flow_parameters()
    else:
        flow = build_flow(conf)
        params = flow_parameters(conf)

    if conf["flags"]["prefect"]["pushToCloudDashboard"]:
        flow.register(project_name="sample")
    else:
        flow.run(parameters=params)

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

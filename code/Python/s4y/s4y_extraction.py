import pandas as pd
from prefect import task, Flow, Parameter
import pysftp
import json
from s4y.s4y_conf import conf
from common.utils import get_working_directory
from common.apis import get_french_schools_data

# Constants
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False
FTP_URL = None
FTP_USER = None
FTP_PASSWORD = None
# Rename items in TARGET_STRUCTURE is ok. Re-ordering implies change some part of coding (where a TARGET_STRUCTURE item is used).
TARGET_STRUCTURE = ["school_id", "scholastic_year", "course_year", "students_number"]
DATA_FILE_NAME = get_working_directory() + "s4y_students_data_fr.csv"

# TODO table écoles
# TODO table étudiants
# TODO concat

@task
def extract_schools_data():
    """
    Extract schools information

    school_id
    """
    df = get_french_schools_data()
    print(df)
    return df


@task
def extract_students_data(url, types):
    """
    Extract data about number of students.

    Parameters
    ----------
    url : str
        URL of the data file containing number of students
    types : dict
        List of names and intended data types of the variables to select
    Returns
    -------
    DataFrame
        The data extracted
    """
    if not types:
        df_students_data = pd.read_csv(url, sep=";")
    else:
        df_students_data = pd.read_csv(url, sep=";", dtype=types,
                                       usecols=types.keys())
    # Rename the two first columns (see TARGET_STRUCTURE and order of parameter "types")
    df_students_data.columns.values[0] = TARGET_STRUCTURE[0]
    df_students_data.columns.values[1] = TARGET_STRUCTURE[1]
    return df_students_data


@task
def transform_students_data_to_df(df_students_data, mapping):
    """
    Transforms data about number of students extracted to dataframe compliant with the target structure.

    Parameters
    ----------
    df_students_data : Dataframe
        Data extracted containing number of students
    mapping : dict
        Mapping between code list of courses year and columns names

    Returns
    -------
    DataFrame
        The data transformed
    """
    # Transform mapping dictionary to dataframe. Get the column name from TARGET_STRUCTURE (course_year)
    df_course_year = pd.DataFrame(list(mapping.keys()),
                                  columns=[TARGET_STRUCTURE[2]])
    # Cartesian product between data and course_year dataframe. Allows us to get all breakdowns
    df_cartesian = pd.merge(df_students_data, df_course_year, how="cross")
    # Create the new variable "students_number"
    df_cartesian[TARGET_STRUCTURE[3]] = -1
    for key, value in mapping.items():
        if len(value) == 1:
            df_cartesian.loc[(df_cartesian[TARGET_STRUCTURE[2]] == key), TARGET_STRUCTURE[3]] = df_cartesian[value[0]]
        else:
            df_cartesian.loc[(df_cartesian[TARGET_STRUCTURE[2]] == key), TARGET_STRUCTURE[3]] = df_cartesian.loc[:, value].sum(axis=1)
    return df_cartesian[TARGET_STRUCTURE]


@task
def concat_datasets(dss):
    return pd.concat(dss, ignore_index=True)


@task
def transform_data_to_csv(df):
    return df.to_csv(DATA_FILE_NAME, index=False, header=True)


@task
def load_file_to_ftp():
    """
    Loads data file created to FTP

    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with open("./code/Python/secrets.json") as sf:
        secrets = json.load(sf)
        FTP_URL = secrets["ftp"]["url"]
        FTP_USER = secrets["ftp"]["user"]
        FTP_PASSWORD = secrets["ftp"]["password"]
    # with pysftp.Connection(FTP_URL, username=FTP_USER, password=FTP_PASSWORD, cnopts=cnopts) as sftp:
    #    with sftp.cd("files/s4y/output"):
    #        sftp.put(DATA_FILE_NAME)


# Build flow
def build_flow():
    with Flow("GF-EF") as flow:
        
        french_schools = extract_schools_data() # WIP

        students_data_url1 = Parameter(name="students_data_url1", required=True)
        types_students_data1 = Parameter(name="types_students_data1", required=True)
        mapping_course_year_columns1 = Parameter(name="mapping_course_year_columns1", required=True)
        french_data_extracted1 = extract_students_data(students_data_url1, types_students_data1)
        french_data1 = transform_students_data_to_df(french_data_extracted1, mapping_course_year_columns1)
        students_data_url2 = Parameter(name="students_data_url2", required=True)
        types_students_data2 = Parameter(name="types_students_data2", required=True)
        mapping_course_year_columns2 = Parameter(name="mapping_course_year_columns2", required=True)
        french_data_extracted2 = extract_students_data(students_data_url2, types_students_data2)
        french_data2 = transform_students_data_to_df(french_data_extracted2, mapping_course_year_columns2)
        students_data_url3 = Parameter(name="students_data_url3", required=True)
        types_students_data3 = Parameter(name="types_students_data3", required=True)
        mapping_course_year_columns3 = Parameter(name="mapping_course_year_columns3", required=True)
        french_data_extracted3 = extract_students_data(students_data_url3, types_students_data3)
        french_data3 = transform_students_data_to_df(french_data_extracted3, mapping_course_year_columns3)
        students_data_url4 = Parameter(name="students_data_url4", required=True)
        types_students_data4 = Parameter(name="types_students_data4", required=True)
        mapping_course_year_columns4 = Parameter(name="mapping_course_year_columns4", required=True)
        french_data_extracted4 = extract_students_data(students_data_url4, types_students_data4)
        french_data4 = transform_students_data_to_df(french_data_extracted4, mapping_course_year_columns4)
        students_data = concat_datasets([french_data1, french_data2, french_data3, french_data4])
        load_file_to_ftp(upstream_tasks=[transform_data_to_csv(students_data)])
    return flow


def main():
    """
    Main entry point for the S4Y pipeline.
    """

    flow = build_flow()
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name="sample")
    else:
        flow.run(parameters={
            "students_data_url1": "https://data.education.gouv.fr/explore/dataset/fr-en-ecoles-effectifs-nb_classes"
                                  "/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true"
                                  "&csv_separator=%3B",
            "types_students_data1": {"Numéro de l'école": str, "Rentrée scolaire": str,
                                     "Nombre d'élèves en pré-élémentaire hors ULIS": int,
                                     "Nombre d'élèves en CP hors ULIS": int, "Nombre d'élèves en CE1 hors ULIS": int,
                                     "Nombre d'élèves en CE2 hors ULIS": int, "Nombre d'élèves en CM1 hors ULIS": int,
                                     "Nombre d'élèves en CM2 hors ULIS": int},
            "mapping_course_year_columns1": {"0": ["Nombre d'élèves en pré-élémentaire hors ULIS"],
                                             "1": ["Nombre d'élèves en CP hors ULIS"],
                                             "2": ["Nombre d'élèves en CE1 hors ULIS"],
                                             "3": ["Nombre d'élèves en CE2 hors ULIS"],
                                             "4": ["Nombre d'élèves en CM1 hors ULIS"],
                                             "5": ["Nombre d'élèves en CM2 hors ULIS"]},
            "students_data_url2": "https://data.education.gouv.fr/explore/dataset/fr-en-college-effectifs-niveau-sexe"
                                  "-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true"
                                  "&csv_separator=%3B",
            "types_students_data2": {"Numéro du collège": str, "Rentrée scolaire": str, "Nombre total de 6èmes": int,
                                     "Nombre total de 5èmes": int, "Nombre total de 4èmes": int,
                                     "Nombre total de 3èmes": int},
            "mapping_course_year_columns2": {"6": ["Nombre total de 6èmes"], "7": ["Nombre total de 5èmes"],
                                             "8": ["Nombre total de 4èmes"], "9": ["Nombre total de 3èmes"]},
            "students_data_url3": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_gt-effectifs-niveau"
                                  "-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header"
                                  "=true&csv_separator=%3B",
            "types_students_data3": {"Numéro du lycée": str, "Rentrée scolaire": str, "2ndes GT": int,
                                     "2ndes STHR": int, "2ndes TMD": int, "2ndes BT": int, "1ères G": int,
                                     "1ères STI2D": int, "1ères STL": int, "1ères STMG": int, "1ères ST2S": int,
                                     "1ères STD2A": int, "1ères STHR": int, "1ères TMD": int, "1ères BT": int,
                                     "Terminales G": int, "Terminales STI2D": int, "Terminales STL": int,
                                     "Terminales STMG": int, "Terminales ST2S": int, "Terminales STD2A": int,
                                     "Terminales STHR": int, "Terminales TMD": int, "Terminales BT": int},
            "mapping_course_year_columns3": {"10": ["2ndes GT", "2ndes STHR", "2ndes TMD", "2ndes BT"],
                                             "11": ["1ères G", "1ères STI2D", "1ères STL", "1ères STMG", "1ères ST2S",
                                                    "1ères STD2A", "1ères STHR", "1ères TMD", "1ères BT"],
                                             "12": ["Terminales G", "Terminales STI2D", "Terminales STL",
                                                    "Terminales STMG", "Terminales ST2S", "Terminales STD2A",
                                                    "Terminales STHR", "Terminales TMD", "Terminales BT"]},
            "students_data_url4": "https://data.education.gouv.fr/explore/dataset/fr-en-lycee_gt-effectifs-niveau"
                                  "-sexe-lv/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header"
                                  "=true&csv_separator=%3B",
            "types_students_data4": {"Numéro du lycée": str, "Rentrée scolaire": str, "2ndes GT": int, "2ndes STHR": int, "2ndes TMD": int, "2ndes BT": int, "1ères G": int, "1ères STI2D": int, "1ères STL": int, "1ères STMG": int, "1ères ST2S": int, "1ères STD2A": int, "1ères STHR": int, "1ères TMD": int, "1ères BT": int, "Terminales G": int, "Terminales STI2D": int, "Terminales STL": int, "Terminales STMG": int, "Terminales ST2S": int, "Terminales STD2A": int, "Terminales STHR": int, "Terminales TMD": int, "Terminales BT": int},
            "mapping_course_year_columns4": {"10": ["2ndes GT", "2ndes STHR", "2ndes TMD", "2ndes BT"],
                                             "11": ["1ères G", "1ères STI2D", "1ères STL", "1ères STMG", "1ères ST2S", "1ères STD2A", "1ères STHR", "1ères TMD", "1ères BT"],
                                             "12": ["Terminales G", "Terminales STI2D", "Terminales STL", "Terminales STMG", "Terminales ST2S", "Terminales STD2A", "Terminales STHR", "Terminales TMD", "Terminales BT"]}
        })

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

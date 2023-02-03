import pandas as pd
from prefect import task, flow
import pysftp
import json
from s4y.s4y_conf import conf
from common.utils import get_working_directory
from common.apis import get_french_schools_data

# Constants
FTP_URL = None
FTP_USER = None
FTP_PASSWORD = None
DATA_FILE_NAME = get_working_directory() + "s4y_data_fr.csv"

# TODO table écoles
# TODO table étudiants
# TODO concat

@task(name="Extract schools data")
def extract_schools_data():
    """
    Extract schools information

    FIXME for now we're only getting:

    "numero_uai AS school_id", "appellation_officielle AS name", "latitude", "longitude", "code_commune AS lau", "secteur_public_prive_libe AS institution_type"

    from the API, some variables are to be computed or grabbed elsewhere.

    See specs here : https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1071249281
    """
    df = get_french_schools_data()
    return df


@task(name="Extract students data")
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
        df_students_data = pd.read_csv(url, sep=";", thousands=" ")
    else:
        df_students_data = pd.read_csv(url, sep=";", dtype=types,
                                       usecols=types.keys(), thousands=" ")
    # TODO: Improve renaming. Here the order of the columns in the file is kept and not in the order of types.keys()
    df_students_data.columns.values[0] = "scholastic_year"
    df_students_data.columns.values[1] = "school_id"
    if not conf["course_year"]:
        df_students_data.columns.values[2] = "students_number"
    return df_students_data


@task(name="Transform schools data")
def transform_schools_data(df_schools_data):
    """
    Transforms data about schools extracted.

    Parameters
    ----------
    df_schools_data : Dataframe
        Data extracted containing list of schools

    Returns
    -------
    DataFrame
        The data transformed
    """
    # Recoding type of institution
    df_schools_data["institution_type"] = df_schools_data["institution_type"].map({"Public": "PU", "Privé": "PR"})
    # Define list of French municipal districts for Lyon, Marseille and Paris
    arm_paris = ["75101", "75102", "75103", "75104", "75105", "75106", "75107", "75108", "75109", "75110", "75111",
                 "75112", "75113", "75114", "75115", "75116", "75117", "75118", "75119", "75120"]
    arm_lyon = ["69381", "69382", "69383", "69384", "69385", "69386", "69387", "69388", "69389"]
    arm_marseille = ["13201", "13202", "13203", "13204", "13205", "13206", "13207", "13208", "13209", "13210", "13211",
                     "13212", "13213", "13214", "13215", "13216"]
    # Add French municipal district in a column if relevant
    df_schools_data["arm"] = df_schools_data["lau"]
    df_schools_data.loc[~df_schools_data["lau"].isin(arm_paris+arm_lyon+arm_paris), "arm"] = ""

    # Switch municipal district for Lyon, Marseille and Paris to Lau code
    df_schools_data.loc[df_schools_data["lau"].isin(arm_paris), "lau"] = "75056"
    df_schools_data.loc[df_schools_data["lau"].isin(arm_lyon), "lau"] = "69123"
    df_schools_data.loc[df_schools_data["lau"].isin(arm_marseille), "lau"] = "13055"
    # Add Isced code
    url = get_working_directory() + "school-registry-mapping-nature-isced.csv"
    df_mapping_nature_isced = pd.read_csv(url, sep=",", usecols=["code_nature", "ISCED_level"])
    df_merged = df_schools_data.merge(df_mapping_nature_isced, left_on="code_nature", right_on="code_nature", how="left")
    return df_merged


@task(name="Transform students data to df")
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
    if conf["course_year"]:
        # Transform mapping dictionary to dataframe. Get the column name from TARGET_STRUCTURE (course_year)
        df_course_year = pd.DataFrame(list(mapping.keys()),
                                  columns=["course_year"])
        # Cartesian product between data and course_year dataframe. Allows us to get all breakdowns
        df_cartesian = pd.merge(df_students_data, df_course_year, how="cross")
        # Create the new variable "students_number"
        df_cartesian["students_number"] = -1
        for key, value in mapping.items():
            if len(value) == 1:
                df_cartesian.loc[(df_cartesian["course_year"] == key), "students_number"] = df_cartesian[value[0]]
            else:
                df_cartesian.loc[(df_cartesian["course_year"] == key), "students_number"] = df_cartesian.loc[:, value].sum(axis=1)
        return df_cartesian[["school_id", "scholastic_year", "course_year", "students_number"]]
    else:
        return df_students_data[["school_id", "scholastic_year", "students_number"]]


@task(name="Concatenate datasets")
def concat_datasets(dss):
    # TODO: check for duplication
    return pd.concat(dss, ignore_index=True)


@task(name="Transform data to CSV")
def transform_data_to_csv(df):
    return df.to_csv(DATA_FILE_NAME, index=False, header=True)


@task(name="Merge datasets")
def merge_datasets(school_ds, students_ds):
    return school_ds.merge(students_ds, left_on="school_id", right_on="school_id", how="left")


@task(name="Load file to ftp")
def load_file_to_ftp():
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
    remote_path = "files/s4y/output/"
    with open("./code/Python/secrets.json") as sf:
        secrets = json.load(sf)
        FTP_URL = secrets["ftp"]["url"]
        FTP_USER = secrets["ftp"]["user"]
        FTP_PASSWORD = secrets["ftp"]["password"]
    # with pysftp.Connection(
    #        FTP_URL, username=FTP_USER, password=FTP_PASSWORD, cnopts=cnopts
    # ) as sftp:
    #    sftp.makedirs(remote_path)  # Create remote path if needed
    #    with sftp.cd(remote_path):
    #        sftp.put(DATA_FILE_NAME)


# Build flow
@flow(name="s4y_api_to_csv")
def s4y_flow():

    french_schools = extract_schools_data()
    french_schools_transformed = transform_schools_data(french_schools)
    students_data_url1 = conf["students_datasets"][0]["csv_url"]
    types_students_data1 = conf["students_datasets"][0]["types"]
    mapping_course_year1 = conf["students_datasets"][0]["mapping_course_year"]
    french_data_extracted1 = extract_students_data(students_data_url1, types_students_data1)
    french_data1 = transform_students_data_to_df(french_data_extracted1, mapping_course_year1)
    students_data_url2 = conf["students_datasets"][1]["csv_url"]
    types_students_data2 = conf["students_datasets"][1]["types"]
    mapping_course_year2 = conf["students_datasets"][1]["mapping_course_year"]
    french_data_extracted2 = extract_students_data(students_data_url2, types_students_data2)
    french_data2 = transform_students_data_to_df(french_data_extracted2, mapping_course_year2)
    students_data_url3 = conf["students_datasets"][2]["csv_url"]
    types_students_data3 = conf["students_datasets"][2]["types"]
    mapping_course_year3 = conf["students_datasets"][2]["mapping_course_year"]
    french_data_extracted3 = extract_students_data(students_data_url3, types_students_data3)
    french_data3 = transform_students_data_to_df(french_data_extracted3, mapping_course_year3)
    students_data_url4 = conf["students_datasets"][3]["csv_url"]
    types_students_data4 = conf["students_datasets"][3]["types"]
    mapping_course_year4 = conf["students_datasets"][3]["mapping_course_year"]
    french_data_extracted4 = extract_students_data(students_data_url4, types_students_data4)
    french_data4 = transform_students_data_to_df(french_data_extracted4, mapping_course_year4)
    students_data = concat_datasets([french_data1, french_data2, french_data3, french_data4])
    french_data = merge_datasets(french_schools_transformed, students_data)
    load_file_to_ftp(wait_for=[transform_data_to_csv(french_data)])


def main():
    """
    Main entry point for the S4Y pipeline.
    """
    s4y_flow()
    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

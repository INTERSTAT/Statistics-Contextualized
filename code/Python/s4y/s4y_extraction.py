import pandas as pd
from prefect import task, Flow, Parameter
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

@task
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
    # TODO: Improve renaming. Here the order of the columns in the file is kept and not in the order of types.keys()
    df_students_data.columns.values[0] = "scholastic_year"
    df_students_data.columns.values[1] = "school_id"
    return df_students_data


@task
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
    # Add Isced code
    url = get_working_directory() + "school-registry-mapping-nature-isced.csv"
    df_mappping_nature_isced = pd.read_csv(url, sep=",", usecols=["code_nature", "ISCED_level"])
    df_merged = df_schools_data.merge(df_mappping_nature_isced, left_on="code_nature", right_on="code_nature", how="left")
    # TODO: Add nuts3 variable based on lau variable?
    return df_merged


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


@task
def concat_datasets(dss):
    # TODO: check for duplication
    return pd.concat(dss, ignore_index=True)


@task
def transform_data_to_csv(df):
    return df.to_csv(DATA_FILE_NAME, index=False, header=True)


@task
def merge_datasets(school_ds, students_ds):
    return school_ds.merge(students_ds, left_on="school_id", right_on="school_id", how="left")


@task
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
def build_flow():
    with Flow("GF-EF") as flow:
        french_schools = extract_schools_data()
        french_schools_transformed = transform_schools_data(french_schools)
        students_data_url1 = Parameter(name="students_data_url1", required=True)
        types_students_data1 = Parameter(name="types_students_data1", required=True)
        mapping_course_year1 = Parameter(name="mapping_course_year1", required=True)
        french_data_extracted1 = extract_students_data(students_data_url1, types_students_data1)
        french_data1 = transform_students_data_to_df(french_data_extracted1, mapping_course_year1)
        students_data_url2 = Parameter(name="students_data_url2", required=True)
        types_students_data2 = Parameter(name="types_students_data2", required=True)
        mapping_course_year2 = Parameter(name="mapping_course_year2", required=True)
        french_data_extracted2 = extract_students_data(students_data_url2, types_students_data2)
        french_data2 = transform_students_data_to_df(french_data_extracted2, mapping_course_year2)
        students_data_url3 = Parameter(name="students_data_url3", required=True)
        types_students_data3 = Parameter(name="types_students_data3", required=True)
        mapping_course_year3 = Parameter(name="mapping_course_year3", required=True)
        french_data_extracted3 = extract_students_data(students_data_url3, types_students_data3)
        french_data3 = transform_students_data_to_df(french_data_extracted3, mapping_course_year3)
        students_data_url4 = Parameter(name="students_data_url4", required=True)
        types_students_data4 = Parameter(name="types_students_data4", required=True)
        mapping_course_year4 = Parameter(name="mapping_course_year4", required=True)
        french_data_extracted4 = extract_students_data(students_data_url4, types_students_data4)
        french_data4 = transform_students_data_to_df(french_data_extracted4, mapping_course_year4)
        students_data = concat_datasets([french_data1, french_data2, french_data3, french_data4])
        french_data = merge_datasets(french_schools_transformed, students_data)
        load_file_to_ftp(upstream_tasks=[transform_data_to_csv(french_data)])
    return flow


def main():
    """
    Main entry point for the S4Y pipeline.
    """
    flow = build_flow()
    if conf["flags"]["prefect"]["pushToCloudDashboard"]:
        flow.register(project_name="s4y")
    else:
        flow.run(parameters={
            "students_data_url1": conf["students_datasets"][0]["csv_url"],
            "types_students_data1": conf["students_datasets"][0]["types"],
            "mapping_course_year1": conf["students_datasets"][0]["mapping_course_year"],
            "students_data_url2": conf["students_datasets"][1]["csv_url"],
            "types_students_data2": conf["students_datasets"][1]["types"],
            "mapping_course_year2": conf["students_datasets"][1]["mapping_course_year"],
            "students_data_url3": conf["students_datasets"][2]["csv_url"],
            "types_students_data3": conf["students_datasets"][2]["types"],
            "mapping_course_year3": conf["students_datasets"][2]["mapping_course_year"],
            "students_data_url4": conf["students_datasets"][3]["csv_url"],
            "types_students_data4": conf["students_datasets"][3]["types"],
            "mapping_course_year4": conf["students_datasets"][3]["mapping_course_year"]})
    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

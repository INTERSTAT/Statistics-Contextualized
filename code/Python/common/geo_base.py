import json
import logging
import time

import pandas as pd
import requests
from prefect import Flow, Parameter, task
from pyproj import Proj, transform, Transformer
from common.utils import get_working_directory, get_resources_directory
from common.common_conf import conf


working_dir = get_working_directory()
USE_LOCAL_FILES = True

# The LAU-NUTS files are taken from https://ec.europa.eu/eurostat/web/nuts/local-administrative-units
# The names of the files for the different years are in the nuts_file_names key of the configuration file


# Functions ----
def get_dep_to_nuts3():
    """
    Returns a dictionary giving the correspondence between French départements and NUTS3.

    Returns:
        dict: A dictionary where keys are department codes and values are corresponding NUTS3 codes.
    """
    # Read the correspondance between departments and NUTS3 and transform it into a dictionary (easier for lookup)
    dep_to_nuts_file = get_resources_directory() + 'dep-nuts3-fr.csv'
    logging.info(f'Loading correspondance between départements and NUTS3 from {dep_to_nuts_file}')
    dep_to_nuts_df = pd.read_csv(dep_to_nuts_file, header=0, dtype='string', usecols=[0, 1], index_col=0)
    temp_dict = dep_to_nuts_df.to_dict('index')
    # temp_dict will be of the form {'01': {'nuts3': 'FRK21'}, '02': {'nuts3': 'FRE21'}, ...}

    return {key: value['nuts3'] for (key, value) in temp_dict.items()}


# Tasks ----
@task(name='Convert coordinates')
def convert_coordinates(frame, lon_column, lat_column, crs_from, crs_to):
    """
    Converts coordinates from on CRS to another.
    See https://pyproj4.github.io/pyproj/stable/api/transformer.html for possible expressions of CRSs.
    See https://spatialreference.org/ for reference naming of CRSs.

    Args
        frame (DataFrame): The data frame containing the coordinates.
        lon_column (str): The name of the column containing the longitude.
        lat_column (str): The name of the column containing the latitude.
        crs_from (Any): The system to transform from.
        crs_to (Any): The system to transform to.
    Returns:
        DataFrame: The input data frame with additional columns 'xy' and 'coord' containing original and converted coordinates.
    """
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    frame["xy"] = frame[[lat_column, lon_column]].apply(tuple, axis=1)
    frame["coord"] = frame["xy"].apply(lambda s: transformer.transform(s[0], s[1]))
    # TODO See possibility to apply directly on two columns, something like the following (which does not work)
    # frame[[lat_column + '_r', lon_column + '_r']] =\
    #     frame[[lat_column, lon_column]].apply(lambda x, y: transformer.transform(x, y), axis=1, result_type='expand')
    # TODO See possibility to pass couples (source and target column names, coordinate systems)

    return frame


@task(name='Add NUTS3 from coordinates')
def add_nuts3_from_coordinates(frame, nuts3_column, lat_column, lon_column, crs='epsg:4326'):
    """Adds in a DataFrame a column with the LAU calculated from existing coordinates.
    The Nominatim API provided by OpenStreetMap (https://nominatim.org) is used

    Args:
        frame (DataFrame): The Pandas data frame to enrich (containing the coordinates).
        nuts3_column (str): Name of the column where the NUTS3 should be written.
        lat_column (str): Name of the column containing the latitude.
        lon_column (str): Name of the column containing the longitude.
        crs (str): Coordinate system used for latitude and longitude.
    Returns:
        DataFrame: The input data frame with an additional nuts3_column containing the NUTS3 code or 'None'.
    """
    url_pattern = 'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2'

    logging.info(f'Enrichment of data frame using Nominatim API with cols {lat_column} and {lon_column}')
    # Get column indexes
    idx_lat = frame.columns.get_loc(lat_column)
    idx_lon = frame.columns.get_loc(lon_column)
    delay = float(conf['nominatisDelay'])

    # Get the dictionary giving the correspondance between départements and NUTS3
    dep_to_nuts3_dict = get_dep_to_nuts3()

    for index, row in frame.iterrows():
        query_url = url_pattern.format(lat=row[idx_lat], lon=row[idx_lon])
        response = requests.get(query_url).json()
        try:
            postcode = response['address']['postcode']
        except KeyError:
            logging.error(f'No postal code in response to query {query_url}')
            frame.loc[index, nuts3_column] = None
            continue
        dep_code = response['address']['postcode'][0:2]
        if dep_code == '97':
            dep_code = response['address']['postcode'][0:3]
        try:
            frame.loc[index, nuts3_column] = dep_to_nuts3_dict[dep_code]
        except KeyError:
            logging.error(f"Département code does not exist: {dep_code}")
            frame.loc[index, nuts3_column] = None
        time.sleep(delay)  # wait a bit before sending the next request

    logging.info('Data with NUTS3 added:')
    logging.info('\n' + str(frame.head(3)))

    return frame


@task(name='Add OSM info')
def add_osm_info(frame, add_column, lat_column, lon_column, crs='epsg:4326'):
    """Adds to a DataFrame a column with OSM information for existing coordinates.
    The Nominatim API provided by OpenStreetMap (https://nominatim.org) is used. See example of information
    returned at https://nominatim.openstreetmap.org/reverse?lat=48.99083&lon=2.444722&format=jsonv2.
    The usage policy at https://operations.osmfoundation.org/policies/nominatim/ should be applied.

    Args:
        frame (DataFrame): The Pandas data frame to enrich (containing the coordinates).
        add_column (str): Name of the column where the LAU should be written.
        lat_column (str): Name of the column containing the latitude.
        lon_column (str): Name of the column containing the longitude.
        crs (str): Coordinate system used for latitude and longitude.
    Returns:
        DataFrame: The input data frame with an additional add_column containing the OSM info.
    """
    url_pattern = 'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2'

    logging.info(f'Enrichment of a data frame using Nominatim API with cols {lat_column} and {lon_column}')
    # Get column indexes
    idx_lat = frame.columns.get_loc(lat_column)
    idx_lon = frame.columns.get_loc(lon_column)
    delay = float(conf["nominatisDelay"])

    for index, row in frame.iterrows():
        query_url = url_pattern.format(lat=row[idx_lat], lon=row[idx_lon])
        frame.loc[index, add_column] = requests.get(query_url).text
        time.sleep(delay)  # wait a bit before sending the next request

    return frame


@task(name='Create LAU-NUTS table')
def get_lau_nuts(ref_year):
    """Creates the LAU-NUTS3 correspondence for a given reference year.

    Args:
        ref_year (str): Reference year.
    Returns:
        DataFrame: Table indexed by LAU with a 'NUTS3' column, containing both French and Italian LAUs.
    Raises:
        AssertionError: If duplicate values of LAU are found in the concatenated table.
    """
    logging.info(f'Creating the LAU-NUTS3 correspondence for year {ref_year}')
    lau_nuts_file_name = conf['nuts_file_names'][str(ref_year)]
    remote_file_url = conf['nuts-ref-base-url'] + lau_nuts_file_name
    local_file_name = working_dir + lau_nuts_file_name

    if not USE_LOCAL_FILES:
        logging.info(f'Downloading from {remote_file_url} and saving to {local_file_name}')
        data = requests.get(remote_file_url)
        with open(local_file_name, 'wb') as file:
            file.write(data.content)

    # NUTS3 is in the first column and LAU in the second
    geo_dfs = pd.read_excel(local_file_name, sheet_name=['FR', 'IT'], dtype=str, usecols=[0, 1], names=['NUTS3', 'LAU'])

    # Merge French and Italian data
    geo_df = pd.concat(geo_dfs)
    # Check uniqueness of LAU values and index the data frame
    assert geo_df['LAU'].is_unique, 'There are duplicate values for the LAU'
    geo_df.set_index('LAU', inplace=True)
    logging.info(f'LAU-NUTS3 correspondence created, {geo_df.shape[0]} LAU found')

    local_csv = working_dir + f'lau-nuts3-{conf["ref-year"]}.csv'
    geo_df.to_csv(local_csv)
    logging.info(f'LAU-NUTS3 correspondence saved to {local_csv}')

    return geo_df


@task(name='Get Italian geography')
def get_lau_nuts_it(url):
    """Creates the LAU-NUTS correspondence for Italy.
    (storing that function in common module but probably useless now)

    Args:
        url (str): URL of the file containing geographic reference data for Italy.
    Returns:
        DataFrame: Table indexed by LAU with 'NUTS3 2010' and 'NUTS3 2021' columns.
    Raises:
        AssertionError: If duplicate values of LAU are found in the source.
    """
    logging.info(f'Reading LAU-NUTS3 correspondence from {url}')
    # LAU expected in column 5, NUTS3 201O in column 23 and NUTS3 2021 in column 26
    geo_it = pd.read_csv(url, encoding='ANSI', sep=';', dtype=str, usecols=[4, 22, 25])
    # Rename columns
    rename_dict = {geo_it.columns[0]: 'LAU', geo_it.columns[1]: 'NUTS3-2010', geo_it.columns[2]: 'NUTS3-2021'}
    # geo_it.rename(columns=rename_dict, inplace=True)
    geo_it.columns = ['LAU', 'NUTS3 2010', 'NUTS3 2021']

    # Check uniqueness of LAU values and index the data frame
    assert geo_it['LAU'].is_unique, 'There are duplicate values for the LAU'
    geo_it.set_index('LAU', inplace=True)
    logging.info(f'LAU-NUTS3 correspondence created, {geo_it.shape[0]} LAU found')

    return geo_it


# Flow and main ----
with Flow('geo_flow') as flow:

    df = pd.DataFrame([[48.862120000000004, 2.3446159999999998], [48.902503999999993, 2.4525000000000001]], columns=['lat', 'lon'])
    df_with_nuts3 = add_nuts3_from_coordinates(frame=df, nuts3_column='nuts3', lat_column='lat', lon_column='lon')


def main():
    logging.basicConfig(filename=get_working_directory() + 'geo-base.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(f'Starting geo_base module, working directory is {working_dir}')
    if conf["flags"]["prefect"]["pushToCloudDashboard"]:
        flow.register(project_name='geo_base')
    else:
        flow.run()

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

# Constants ----
import json
import logging
import time

import pandas as pd
import requests
from prefect import Flow, Parameter, task
from pyproj import Proj, transform, Transformer
from common.utils import get_working_directory
from common.common_conf import conf


WORK_DIRECTORY = '../../../work/'
USE_LOCAL_FILES = True

REF_YEAR = '2019'

# The LAU-NUTS files are taken from https://ec.europa.eu/eurostat/web/nuts/local-administrative-units
# The names of the files for the different years are in the GEO_FILE_NAMES JSON file
GEO_FILE_NAMES = '../../../pilots/resources/geo_files.json'
BASE_URL = 'https://ec.europa.eu/eurostat/documents/345175/501971/'
LOCAL_CSV = WORK_DIRECTORY + f'lau-nuts3-{REF_YEAR}.csv'


# Tasks ----
@task(name='Convert coordinates')
def convert_coordinates(frame, lon_column, lat_column, crs_from, crs_to):
    """
    See https://spatialreference.org/
    :param crs_from:
    :param crs_to:
    :param lon_column:
    :param lat_column:
    :type frame: DataFrame
    """
    transformer = Transformer.from_crs(crs_from, crs_to, always_xy=True)
    frame["xy"] = frame[[lat_column, lon_column]].apply(tuple, axis=1)
    frame["coord"] = frame["xy"].apply(lambda s: transformer.transform(s[0], s[1]))
    # TODO See possibility to apply directly on two columns, something like the following (which does not work)
    # frame[[lat_column + '_r', lon_column + '_r']] =\
    #     frame[[lat_column, lon_column]].apply(lambda x, y: transformer.transform(x, y), axis=1, result_type='expand')
    # TODO See possibility to pass couples (source and target column names, coordinate systems)

    return frame


@task(name='Coordinates to LAU')
def coordinates_to_lau(frame, lau_column, lat_column, lon_column, crs='epsg:4326'):
    """Adds in a DataFrame a column with the LAU calculated from existing coordinates.
    The Nominatim API provided by OpenStreetMap (https://nominatim.org) is used

    Args:
    frame (DataFrame): The Pandas data frame to enrich (containing the coordinates).
    lau_column (str): Name of the column where the LAU should be written.
    lat_column (str): Name of the column containing the latitude.
    lon_column (str): Name of the column containing the longitude.
    crs (str): Coordinate system used for latitude and longitude.
    """
    url_pattern = 'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2'

    logging.info(f'Enrichment of data frame using Nominatim API with cols {lat_column} and {lon_column}')
    # Get column indexes
    idx_lat = frame.columns.get_loc(lat_column)
    idx_lon = frame.columns.get_loc(lon_column)
    delay = float(conf["nominatisDelay"])

    for index, row in frame.iterrows():
        query_url = url_pattern.format(lat=row[idx_lat], lon=row[idx_lon])
        response = requests.get(query_url).json()
        print(response['address'])
        time.sleep(delay)  # wait a bit before sending the next request

    # In the case of France, Nominatim provides the postal code (country_code": "fr") which has to be translated to LAU
    return


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
    with open(GEO_FILE_NAMES) as geo_json:
        file_names = json.load(geo_json)
        file_name = file_names["file_names"][ref_year]
        remote_file_url = BASE_URL + file_name
        local_file_name = WORK_DIRECTORY + file_name

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

    geo_df.to_csv(LOCAL_CSV)
    logging.info(f'LAU-NUTS3 correspondence saved to {LOCAL_CSV}')

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


with Flow('test_flow') as flow:

    df = pd.DataFrame([[48.862120000000004, 2.3446159999999998], [48.902503999999993, 2.4525000000000001]], columns=['lat', 'lon'])
    coordinates_to_lau(frame=df, lau_column='lau', lat_column='lat', lon_column='lon')


def main():
    logging.basicConfig(filename=get_working_directory() + 'geo-base.log', encoding='utf-8', level=logging.DEBUG)
    if conf["flags"]["prefect"]["pushToCloudDashboard"]:
        flow.register(project_name='geo_base')
    else:
        flow.run()

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

from io import BytesIO, StringIO

from prefect import task, Flow, Parameter
from requests import get
import pandas as pd
import logging

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

FTP_URL = 'FTP_URL'
FTP_USERNAME = 'FTP_USERNAME'
FTP_PASSWORD = 'FTP_PASSWORD'

WORK_DIRECTORY = "../../../work/"
USE_LOCAL_FILES = True
VISUALIZE_FLOW = False

REF_YEAR = '2019'

# Tasks ----


@task(name='Get air quality data from API')
def extract_aq_api(pollutant):
    """Extracts data on air quality from the EEA API.

    Args:
        pollutant (str): name of the pollutant for which the data is fetched.
    Returns:
        DataFrame: Table containing the measures of air quality for the pollutant.
    """
    logging.info(f'Reading air quality data for pollutant: {pollutant}')
    country = 'France'  # Should also be in fist column
    with open('aq-query.txt', 'r') as file:
        query_url = file.read().format(country=country, year=REF_YEAR, pollutant=pollutant)

    logging.info(f'About to GET: {query_url}')
    # The following query dies horribly if 'dtype' is omitted, whereas it works on a local copy of the data
    aq_api = pd.read_csv(query_url, header=1, usecols=[3, 5, 6, 18], dtype=str,
                         names=['StationID', 'Latitude', 'Longitude', 'AQValue'])
    logging.info('Data retrieved:')
    logging.info(aq_api.head(3))

    return aq_api


@task(name='Extract French air quality data')
def extract_french_aq(url):
    """Extracts the French data on air quality.
    Placeholder for now.

    Args:
        url (str): URL of the file containing the data.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """
    logging.info(f'Reading French air quality data from {url}')
    new_cols = {'POLLUTANT': 'PM10', 'AGGREGATION_TYPE': 'Annual mean', 'REPORTING_YEAR': '2019'}
    aq_fr_raw = pd.read_csv(url, header=1, usecols=[3, 5, 6, 18],
                            names=['StationID', 'Latitude', 'Longitude', 'AQValue']).assign(**new_cols)

    print(aq_fr_raw)
    return aq_fr_raw


@task(name='Get Italian geography')
def get_lau_nuts_it(url):
    """Creates the LAU-NUTS correspondence for Italy.

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


@task(name='Extract Italian air quality data')
def extract_italian_aq(url, geo_it):
    """Extracts the Italian data on air quality.

    Args:
        url (str): URL of the file containing the data.
        geo_it (DataFrame): table containing the correspondance between LAU and NUTS3.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """
    logging.info(f'Reading Italian air quality data from {url}')
    new_cols = {'POLLUTANT': 'PM10', 'AGGREGATION_TYPE': 'Annual mean', 'REPORTING_YEAR': '2019'}
    aq_it_raw = pd.read_excel(url, sheet_name='PM10 def', usecols=[2, 11], names=['LAU', 'AQValue']).assign(**new_cols)
    # LAU values are not standard and have to be corrected: convert to string and keep last 6 characters
    aq_it_raw['LAU'] = aq_it_raw['LAU'].map(lambda x: str(x)[-6:])
    logging.info(f'Air quality data table created with {aq_it_raw.shape[0]} lines')

    # Get the correspondence between LAU and NUTS3 (choosing NUTS3 2021 here)
    lau_nuts_it = geo_it.drop(columns=['NUTS3 2010'])
    lau_nuts_it.rename(columns={'NUTS3 2021': 'NUTS3'}, inplace=True)

    # Merge on LAU to add NUTS3
    aq_it = aq_it_raw.merge(lau_nuts_it, left_on='LAU', right_index=True)

    return aq_it


with Flow('aq_csv_to_rdf') as flow:

    prefix_aq_fr = prefix_aq_it = prefix_geo_it = WORK_DIRECTORY
    if not USE_LOCAL_FILES:
        prefix_aq_it = 'https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/448/'
        prefix_geo_it = 'https://www.istat.it/storage/codici-unita-amministrative/'

    french_aq_data_url = Parameter('fr_url', default=prefix_aq_fr + 'sep-aq_fr.csv')
    # french_aq = extract_french_aq(french_aq_data_url)
    # french_aq = extract_aq_api(pollutant='Particulate+matter+%3C+10+%C2%B5m+(aerosol)')
    french_aq = extract_aq_api(pollutant='Nitrogen%20dioxide%20(air)')

    # italian_aq_data_url = Parameter('it_url', default=prefix_aq_it + 'TABELLA 1_PM10_2019_rev.xlsx')
    # italian_geo_url = Parameter('it_geo_url', default=prefix_geo_it + 'Elenco-comuni-italiani.csv')
    # italian_aq = extract_italian_aq(italian_aq_data_url, get_lau_nuts_it(italian_geo_url))
    # extract_aq_api(french_aq_data_url)


if __name__ == '__main__':
    logging.basicConfig(filename=WORK_DIRECTORY + 'sep-aq.log', encoding='utf-8', level=logging.DEBUG)
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep-aq')
    else:
        flow.run()

    if VISUALIZE_FLOW:
        flow.visualize()

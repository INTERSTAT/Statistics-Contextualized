from prefect import task, Flow, Parameter
import pandas as pd
import logging

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

FTP_URL = 'FTP_URL'
FTP_USERNAME = 'FTP_USERNAME'
FTP_PASSWORD = 'FTP_PASSWORD'

WORK_DIRECTORY = "../../../work/"
VISUALIZE_FLOW = False

# Tasks ----


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

    # italian_aq_data_url = Parameter('it_url', default='https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/448/TABELLA%201_PM10_2019_rev.xlsx')
    # italian_geo_url = Parameter('it_geo_url', 'default=https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv')
    italian_aq_data_url = Parameter('it_url', default=WORK_DIRECTORY + 'TABELLA 1_PM10_2019_rev.xlsx')
    italian_geo_url = Parameter('it_geo_url', default=WORK_DIRECTORY + 'Elenco-comuni-italiani.csv')
    italian_aq = extract_italian_aq(italian_aq_data_url, get_lau_nuts_it(italian_geo_url))


if __name__ == '__main__':
    logging.basicConfig(filename=WORK_DIRECTORY + 'sep-aq.log', encoding='utf-8', level=logging.DEBUG)
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep-aq')
    else:
        flow.run()

    if VISUALIZE_FLOW:
        flow.visualize()

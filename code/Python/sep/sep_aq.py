import json
import urllib

from prefect import task, Flow
import pandas as pd
import logging

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

FTP_URL = 'FTP_URL'
FTP_USERNAME = 'FTP_USERNAME'
FTP_PASSWORD = 'FTP_PASSWORD'

WORK_DIRECTORY = "../../../work/"
USE_LOCAL_FILES = True

REF_YEAR = '2019'

with open('../sep/sep.conf.json') as conf_str:
    conf = json.load(conf_str)

logging.basicConfig(filename=WORK_DIRECTORY + 'sep-aq.log', encoding='utf-8', level=logging.DEBUG)

# Tasks ----


@task(name='Get air quality data from EEA')
def extract_aq_eea(pollutant, country, local):
    """Extracts data on air quality from the EEA API.

    Args:
        pollutant (dict): pollutant for which the data is fetched.
        country (str): country for which the data is fetched.
        local (boolean): indicates if locally cached API results are used.
    Returns:
        DataFrame: Table containing the measures of air quality for the given pollutant and country.
    """
    logging.info(f'Fetching air quality data for pollutant {pollutant["name"]} and country {country}')
    if local:
        url = WORK_DIRECTORY + pollutant["cache"]
    else:
        with open('aq-query.txt', 'r') as file:
            url = file.read().format(country=country, year=REF_YEAR, pollutant=pollutant["query-name"])

    logging.info(f'About to read data from: {url}')
    # The following query dies horribly for API if 'dtype' is omitted, whereas it works on a local copy of the data
    aq_eea = pd.read_csv(url, header=1, usecols=[0, 3, 5, 6, 8, 18], dtype=str,
                         names=['Country', 'StationID', 'Latitude', 'Longitude', 'AGType', 'AQValue'])
    logging.info('Data retrieved:')
    logging.info('\n' + str(aq_eea.head(3)))

    return aq_eea


@task(name='Extract French air quality data')
def extract_french_aq(local=True):
    """Extracts the French data on air quality for all pollutants.
    For France, air quality data is obtained through the EEA API (or local cache of the results).

    Args:
        local (boolean): indicates if locally cached API results are used.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """
    logging.info('Reading EEA data for French air quality from ' + 'local cache' if local else 'API')
    frames = []
    for pollutant in conf["pollutants"]:
        logging.info(f'Reading French air quality data for pollutant {pollutant["id"]}')
        new_cols = {'Pollutant': pollutant['id'], 'ReportingYear': REF_YEAR}
        frames.append(extract_aq_eea.run(pollutant=pollutant, country='France', local=local).assign(**new_cols))
    french_aq_df = pd.concat(frames)
    logging.info('Data retrieved:')
    logging.info('\n' + str(french_aq_df.head(3)) + '\n...\n' + str(french_aq_df.tail(3)))
    return french_aq_df


@task(name='Get air quality data from Ispra')
def extract_aq_ispra(pollutant, local):
    """Extracts data on air quality from the data on the Ispra web site.
    Here, the country value will be constantly equal to 'Italy'

    Args:
        pollutant (dict): pollutant for which the data is fetched.
        local (boolean): indicates if locally cached data files are used.
    Returns:
        DataFrame: Table containing the measures of air quality for Italy and the given pollutant.
    """
    if local:
        path = WORK_DIRECTORY + pollutant['ispra-name']
    else:
        path = pollutant['ispra-base'] + urllib.parse.quote(pollutant['ispra-name'])
    logging.info(f'About to read Ispra data for Italian air quality from {path}')
    # Municipality code and station identifier are always in columns C and D, pollutant mostly in column K
    # but for PM10 the medium value is in column L, and for Ozone K is just one of multiple measures
    columns = [2, 3, 10]
    if pollutant["id"] == '10':
        columns[2] = 11
    # new_cols = {'Pollutant': pollutant['id'], 'ReportingYear': REF_YEAR}
    # TODO Next sentence raises certificate error when using remote source, might have to use requests.get with verify=False
    aq_ispra = pd.read_excel(path, header=1, usecols=columns, dtype=str, names=['Municipality', 'StationID', 'AQValue'])
    # Municipality codes are not standard LAU values and have to be corrected: keep last 6 characters
    aq_ispra['LAU'] = aq_ispra['Municipality'].map(lambda x: str(x)[-6:])
    logging.info('Data retrieved:')
    logging.info('\n' + str(aq_ispra.head(3)))

    return aq_ispra


@task(name='Extract Italian air quality data')
def extract_italian_aq(local=True):
    """Extracts the Italian data on air quality.

    Args:
        local (boolean): indicates if locally cached API results are used.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """
    logging.info('Reading Ispra data for Italian air quality from ' + 'local cache' if local else 'web site')
    frames = []
    for pollutant in conf["pollutants"]:
        logging.info(f'Reading Italian air quality data for pollutant {pollutant["id"]}')
        new_cols = {'Pollutant': pollutant['id'], 'ReportingYear': REF_YEAR}
        frames.append(extract_aq_ispra.run(pollutant=pollutant, local=local).assign(**new_cols))
    italian_aq_df = pd.concat(frames)
    logging.info('Data retrieved:')
    logging.info('\n' + str(italian_aq_df.head(3)) + '\n...\n' + str(italian_aq_df.tail(3)))

    return italian_aq_df


with Flow('aq_csv_to_rdf') as flow:

    # french_ex = extract_aq_eea(pollutant=conf['pollutants'][1], country='France', local=True)
    french_aq = extract_french_aq(local=True)
    # italian_ex = extract_aq_ispra(pollutant=conf['pollutants'][1], local=True)
    italian_aq = extract_italian_aq(local=True)


if __name__ == '__main__':

    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', None)
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep-aq')
    else:
        flow.run()

    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

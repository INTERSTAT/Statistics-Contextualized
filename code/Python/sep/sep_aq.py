import urllib
from prefect import task, flow
import pandas as pd
import logging
from sep.sep_conf import conf
from common.utils import get_working_directory
from common.geo_base import add_nuts3_from_coordinates, add_osm_info

# Constants ----
REF_YEAR = conf["ref-year"]


# Extraction Tasks ----
@task(name='Get EEA data for a pollutant and a country')
def extract_aq_eea(pollutant, country, local):
    """Get data on air quality from the EEA API for one pollutant and one country.

    Args:
        pollutant (dict): pollutant for which the data is fetched.
        country (str): country for which the data is fetched.
        local (boolean): indicates if locally cached API results are used.
    Returns:
        DataFrame: Table containing the measures of air quality for the given pollutant and country.
    """
    logging.info(f'Fetching air quality data for pollutant {pollutant["name"]} and country {country}')
    if local:
        url = get_working_directory() + pollutant["cache"]
    else:
        url = conf["aq_query"].format(country=country, year=REF_YEAR, pollutant=pollutant["query-name"])
    logging.info(f'About to read data from: {url}')

    # The following query dies horribly for API if 'dtype' is omitted, whereas it works on a local copy of the data
    aq_eea = pd.read_csv(url, header=1, usecols=[0, 3, 5, 6, 8, 18], dtype=str,
                         names=['Country', 'StationID', 'Latitude', 'Longitude', 'AGType', 'AQValue'])
    logging.info('Data retrieved:')
    logging.info('\n' + str(aq_eea.head(3)))

    return aq_eea


@task(name='Get EAA data for a country')
def extract_country_aq(country, local=True):
    """Get data on air quality from the EEA API for one country and all pollutants.

    Args:
        local (boolean): indicates if locally cached API results are used.
        country (str): country for which the data is fetched.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """
    logging.info(f'Reading EEA data for {country} from ' + 'local cache' if local else 'API')
    frames = []
    for pollutant in conf["pollutants"]:
        logging.info(f'Reading air quality data for pollutant {pollutant["id"]}')
        new_cols = {'Pollutant': pollutant['id'], 'ReportingYear': REF_YEAR}
        frames.append(extract_aq_eea.run(pollutant=pollutant, country=country, local=local).assign(**new_cols))
    country_aq_df = pd.concat(frames)
    logging.info('\n\nData retrieved:')
    logging.info('\n' + str(country_aq_df.head(3)) + '\n...\n' + str(country_aq_df.tail(3)))
    return country_aq_df


@task(name='Extract French air quality data')
def extract_french_aq(local=True):
    """Extracts the French data on air quality for all pollutants.
    For France, air quality data is obtained through the EEA API (or local cache of the results).

    Args:
        local (boolean): indicates if locally cached API results are used.
    Returns:
        DataFrame: Table containing the measures of air quality.
    """

    return extract_country_aq.run('France', local)


@task(name='Get air quality data from Ispra')
def extract_aq_ispra(pollutant, local):
    """Extracts data on air quality from the data on the Ispra website.
    Here, the country value will be constantly equal to 'Italy'

    Args:
        pollutant (dict): pollutant for which the data is fetched.
        local (boolean): indicates if locally cached data files are used.
    Returns:
        DataFrame: Table containing the measures of air quality for Italy and the given pollutant.
    """
    if local:
        path = get_working_directory() + pollutant['ispra-name']
    else:
        path = pollutant['ispra-base'] + urllib.parse.quote(pollutant['ispra-name'])
    logging.info(f'About to read Ispra data for Italian air quality from {path}')
    # Municipality code and station identifier are always in columns C and D, pollutant mostly in column K
    # but for PM10 the medium value is in column L, and for Ozone K is just one of multiple measures
    columns = [2, 3, 10]
    if pollutant["id"] == 'PM10':
        columns[2] = 11
    new_names = ['Municipality', 'StationID', 'AQValue']
    new_cols = {'Pollutant': pollutant['id'], 'ReportingYear': REF_YEAR, 'Country': 'Italy'}
    # TODO Next sentence raises certificate error when using remote source, might have to use requests.get with verify=False
    aq_ispra = pd.read_excel(path, header=1, usecols=columns, dtype=str, names=new_names).assign(**new_cols)
    # Municipality codes are not standard LAU values and have to be corrected: keep last 6 characters
    aq_ispra['LAU'] = aq_ispra['Municipality'].map(lambda x: str(x)[-6:])
    logging.info(f'\n\nData retrieved for pollutant {pollutant["name"]}:')
    logging.info('\n' + str(aq_ispra.head(3)))

    return aq_ispra


@task(name='Extract Italian air quality data')
def extract_italian_aq(local=True):
    """Extracts the Italian data on air quality from Ispra source.

    Args:
        local (boolean): indicates if locally cached Ispra data are used.
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


@task(name='Extract air quality data for all countries and pollutants')
def extract_aq_data(local=True):
    """Extracts the data on air quality for all countries and all pollutants.

    Args:
        local (boolean): indicates if locally cached data should be used.
    Returns:
        Dictionary: A map between a country name (key as string) and the air quality data (value as DataFrame).
    """
    logging.info('Reading data on air quality from ' + 'local cache' if local else 'the web')
    # First create a dictionary of the datasets by country
    aq_data = dict()
    # Unless Italy is in the countries_eea list, read Italian data from Ispra
    if 'Italy' in conf["countries_eea"]:
        aq_data['Italy'] = extract_italian_aq(local)
    for country in conf["countries_eea"]:
        aq_data[country] = extract_country_aq(country, local)

    return aq_data


@task(name='Sample air quality data')
def sample_aq_data(complete_data):
    try:
        size = conf['aq_sample_size']
        logging.info(f'Sampling {size} records from data frame')
        return complete_data.sample(size)
    except KeyError:
        return complete_data


# Transformation Tasks ----
@task(name='Transform EEA data to common format')
def transform_eea_data(eea_data):
    logging.info(f'Starting the transformation of EEA data to the target format, initial shape is {eea_data.shape}')
    # Transformation of EEA data consists in adding a NUTS3 column
    # First we deduplicate the list of stations and their coordinates to minimize Nominatim usage, then add NUTS3
    stations = eea_data[['StationID', 'Latitude', 'Longitude']].drop_duplicates(subset=['StationID'])  # Will use keep='first' default value
    logging.info(f'List of stations extracted, number of stations: {eea_data.shape[0]}')
    # Add a 'NUTS3' column
    stations_with_nuts3 = add_nuts3_from_coordinates.run(stations, 'NUTS3', 'Latitude', 'Longitude')[['StationID', 'NUTS3']]
    # Join with original data frame on station identifier
    eea_data_with_nuts3 = pd.merge(left=eea_data, right=stations_with_nuts3, on='StationID', sort=False)

    logging.info(f'Data after addition of NUTS3 (shape {eea_data_with_nuts3.shape}):')
    logging.info('\n' + str(eea_data_with_nuts3.head(3)))
    return eea_data_with_nuts3


@task(name='Transform Ispra data to common format')
def transform_ispra_data():
    logging.info('Starting the transformation of Ispra data to the target format')
    return


@task(name='Merge data from EEA and Ispra')
def merge_data():
    logging.info('Starting the merging of EEA and Ispra')
    return


@task(name='Enrich stations')
def enrich_stations(frame, id_column, res_column, lat_column, lon_column, crs='epsg:4326'):
    """Enrich a data frame containing geolocalized stations with addresses from the Nominatis API.

    Args:
    frame (DataFrame): The Pandas data frame to enrich (containing the coordinates).
    id_column (str): Name of the column where containing the identifiers (on which deduplication will be made).
    res_column (str): Name of the column where the Nominatis results should be written (as a string).
    lat_column (str): Name of the column containing the latitude.
    lon_column (str): Name of the column containing the longitude.
    crs (str): Coordinate system used for latitude and longitude.
Returns:
    DataFrame: The input data frame with an additional 'res_column' column containing the results of enrichment.
"""
    # First deduplicate the data frame on the identifier column, keeping only identifier and coordinates
    logging.info('Enriching data identified by ' + id_column)
    stations = frame[id_column, lat_column, lon_column].drop_duplicates(subset=[id_column])  # Will use keep='first' default value

    return add_osm_info(stations, 'nominatim_res', lat_column, lon_column)


# Loading Tasks ----
@task(name='Load to FTP server')
def load_to_ftp():
    # Duplicate write_csv_on_ftp from sep-census (or better, move it to common)
    logging.info('Uploading data to FTP')
    return


@task(name='Load to triple store')
def load_to_graphdb():
    logging.info('Uploading data to triple store')
    return


# Flow and main ----
@flow(name="aq_csv_to_rdf")
def sep_aq_flow():
    # working_dir = Parameter(name="working_dir", default=get_working_directory(), required=True)
    logging.basicConfig(filename=get_working_directory() + 'sep-aq.log', encoding='utf-8', level=logging.DEBUG)
    french_aq = sample_aq_data(extract_french_aq(local=True))
    italian_aq = extract_italian_aq(local=True)
    french_aq_transformed = transform_eea_data(french_aq)


def main():
    """
    Main entry point for the SEP-AQ pipeline.
    """
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', None)
    sep_aq_flow()
    if conf["flags"]["prefect"]["displayGraphviz"]:
        flow.visualize()

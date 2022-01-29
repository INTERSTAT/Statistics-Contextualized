from prefect import task, Flow, Parameter
import pandas as pd

# Constants ----
PUSH_TO_PREFECT_CLOUD_DASHBOARD = False

FTP_URL = 'FTP_URL'
FTP_USERNAME = 'FTP_USERNAME'
FTP_PASSWORD = 'FTP_PASSWORD'

WORK_DIRECTORY = "../../../work/"
VISUALIZE_FLOW = True

# Tasks ----

@task
def extract_italian_aq(url):

    new_cols = {'POLLUTANT': 'PM10', 'AGGREGATION_TYPE': 'Annual mean', 'REPORTING_YEAR': '2019'}
    df = pd.read_excel(url, sheet_name='PM10 def', usecols=[2, 11], names=['LAU', 'AQValue']).assign(**new_cols)
    # At this stage, types are int64 for LAU and object for AQValue and added columns
    # LAU values are not standard and have to be corrected: convert to string and keep last 6 characters
    df['LAU'] = df['LAU'].map(lambda x: str(x)[-6:])

    return df


with Flow('census_csv_to_rdf') as flow:

    # italian_aq_data_url = Parameter('it_url', default='https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/448/TABELLA%201_PM10_2019_rev.xlsx')
    italian_aq_data_url = Parameter('it_url', default=WORK_DIRECTORY + 'TABELLA 1_PM10_2019_rev.xlsx')
    italian_aq = extract_italian_aq(italian_aq_data_url)


if __name__ == '__main__':
    if PUSH_TO_PREFECT_CLOUD_DASHBOARD:
        flow.register(project_name='sep-aq')
    else:
        flow.run()

    if VISUALIZE_FLOW:
        flow.visualize()

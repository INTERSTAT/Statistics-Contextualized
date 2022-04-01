"""
Technical configuration for the common module.
"""

conf = {
    "flags": {
        "prefect": {
            "pushToCloudDashboard": False,
            "displayGraphviz": False
        },
        "flow": {
            "testing": True
        }
    },
    "env": {
        "workingDirectory": ""
    },
    "ref-year": 2019,
    "nuts-ref-base-url": "https://ec.europa.eu/eurostat/documents/345175/501971/",
    "nuts_file_names": {
            "2021": "EU-27-LAU-2021-NUTS-2021.xlsx",
            "2020": "EU-27-LAU-2020-NUTS-2021-NUTS-2016.xlsx",
            "2019": "EU-28-LAU-2019-NUTS-2016.xlsx",
            "2018": "EU-28-LAU-2018-NUTS-2016.xlsx",
            "2017": "EU-28_LAU_2017_NUTS_2016.xlsx"
        },
    "nominatisDelay": 1.5
}

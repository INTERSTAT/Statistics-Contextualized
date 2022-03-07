"""
Technical configuration for the GF pipeline.
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
    "countries": ["France"],
    "pollutants": [
        {
            "id": "NO2",
            "name": "Nitrogen dioxide",
            "query-name": "Nitrogen%20dioxide%20(air)",
            "cache": "sep-aq_fr_NO2.csv",
            "ispra-base": "https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/450/",
            "ispra-name": "TABELLA1_NO2_2019.xlsx"
        },
        {
            "id": "O3",
            "name": "Ozone",
            "query-name": "Ozone%20(air)",
            "cache": "sep-aq_fr_O3.csv",
            "ispra-base": "https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/451/",
            "ispra-name": "TABELLA 1_O3_SALUTE_2019.xlsx"
        },
        {
            "id": "PM10",
            "name": "Particulate matter 10",
            "query-name": "Particulate+matter+%3C+10+%C2%B5m+(aerosol)",
            "cache": "sep-aq_fr_PM10.csv",
            "ispra-base": "https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/448/",
            "ispra-name": "TABELLA 1_PM10_2019_rev.xlsx"
        },
        {
            "id": "PM2.5",
            "name": "Particulate matter 2.5",
            "query-name": "Particulate+matter+%3C+2.5+%C2%B5m+(aerosol)",
            "cache": "sep-aq_fr_PM2.5.csv",
            "ispra-base": "https://annuario.isprambiente.it/sites/default/files/sys_ind_files/indicatori_ada/452/",
            "ispra-name": "TABELLA 1_PM25_2019_rev_0.xlsx"
        }
    ]
}

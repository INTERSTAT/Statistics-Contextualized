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
    "nominatisDelay": 0.5
}

"""
Technical configuration for the S4Y pipeline.
"""

conf = {
    "flags": {
        "prefect": {
            "pushToCloudDashboard": False,
            "displayGraphviz": False
        },
        "flow": {
            "testing": False
        }
    },
    "env": {
        "workingDirectory": ""
    }
}

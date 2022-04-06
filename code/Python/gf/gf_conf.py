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
    }
}

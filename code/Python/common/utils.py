import json


def get_conf(conf_path=None):
    """
    Gets the configuration stored in a JSON file.
    """
    with open(conf_path) as conf_str:
        return json.load(conf_str)

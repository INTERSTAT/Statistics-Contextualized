import json
import os
import pathlib


def get_conf(conf_path=None):
    """
    Gets the configuration stored in a JSON file.
    """
    with open(conf_path) as conf_str:
        return json.load(conf_str)


def get_working_directory(conf=None):
    """
    If there is a working dir in the conf file, returns it, else returns a default one.
    """
    if conf is None or conf["env"]["workingDirectory"] == "":
        project_path = pathlib.Path(__file__).cwd()
        wd = str(project_path) + "/work/"
        os.makedirs(wd, exist_ok=True)
        return wd
    else:
        return conf["env"]["workingDirectory"]
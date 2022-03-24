# Data pipelines


## Local execution

### Set up Python

 - Install [Anaconda](https://docs.anaconda.com/anaconda/install/)

### Create virtual environment

 - Launch the Anaconda Prompt
 - Optionally, update conda to the latest version: `conda update conda`
 - Create a dedicated virtual environment: `conda create --name interstat`
 - Activate the new environment: `conda activate interstat`

### Install packages

 - Install [Prefect](https://docs.prefect.io/core/getting_started/install.html): `conda install -c conda-forge prefect`
 - Install [flow visualization tools](https://docs.prefect.io/core/advanced_tutorials/visualization.html): `pip install "prefect[viz]"`
 - Install [pandas](https://pandas.pydata.org/docs/getting_started/install.html): `conda install -c conda-forge pandas`
 - Install [pysftp](https://pypi.org/project/pysftp/): `conda install -c conda-forge pysftp`
 - Install [RDFLib](https://rdflib.readthedocs.io/en/stable/): `pip install rdflib`
 - Install [pyproj](https://github.com/pyproj4/pyproj): `conda install -c conda-forge pyproj`

Notes:
 - the flow visualization tools rely on [Graphviz](https://graphviz.org/)
 - installing RDFLib with conda fails because RDFLib requires Python version to be strictly below 3.10, which is the version installed when conda installs Prefect.

### Configure credentials

Copy the `secrets.json` file in the `code\Python` folder.

### Running pipelines

Each package is a module on its own, discovered via the `setup.py` program.

In order to run a specific pipeline:

- be sure you have activated the conda environment
- place your favorite terminal at the root directory for Statistics-Contextualized
- run the chosen launch script
  - for example, the Global Facilities use case: `python .\code\Python\gf_run.py`
  - in some execution, you might want to pay attention to the launch directory
    - in IntelliJ, for example, you will need to modify the `Working directory` field of your Run configuration in order to have it target the _Statistics contextualised_ Git project root.

Some pipelines will need files in the `work` directory, be sure to have it created and populated accordingly to the pipeline documentation.

#### Proxy issues

For some reason at Insee, on some desktop configurations there is a noisy `no_proxy` env var that causes troubles. The best is to remove this pain point by  `set no_proxy=`- for example in your terminal before launching a script.

### Connect IDE to virtual environment

#### Spyder

The [Spyder IDE](https://www.spyder-ide.org/) comes with Anaconda and can be used to edit the Python scripts in the dedicated Python virtual environment. In the “Tools / Preferences” window, click on “Python interpreter” and select the `interstat` Python interpreter in the “Use the following Python interpreter” drop-down list.

#### IntelliJ IDEA

IntelliJ can be used to edit the Python scripts with the “Python Community Edition” plugin. In the project settings (F4 in the Project tool window), click on “Add SDK / Python SDK” in the “SDK:” drop-down list, then “Conda Environment / Existing environment” and chose the `interstat` Python interpreter.

#### Visual Studio Code

The [VSCode documentation](https://code.visualstudio.com/docs/python/environments) details how to select a Python interpreter in the Command Palette (Ctrl+Shift+P). 

### Code style

Use [black](https://github.com/psf/black) for formatting either:

 - using as a command line: `black file-to-format.py`
 - integrated in VS Code (with "format on save" if possible)

Install globally with `pip install black` or `conda install black`.
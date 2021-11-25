# SEP

This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See description [here](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep).

## Setup

Install `prefect`, `rdflib` & `pysftp` 

```sh
conda install -c conda-forge prefect
pip install rdflib
pip install pysftp
```

## Ftp

Provide FTP host & credentials
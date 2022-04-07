# Geolocalized Facilities (GF) Interstat pilot

## Data

### French data
The central source of french data for this pilot is the Permanent database of facilities ([BPE](https://www.insee.fr/en/metadonnees/source/serie/s1161) in French) published by Insee. For a working example, we extract a list of columns from the CSV file containing the data from the 2020 edition of the database.

BPE data and metatadata are available in CSV formats from the BPE [landing page](https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656). More specifically, the example uses an extract of the following geocoded facilities:
- (dataset 1) Exposition venues and heritage, file available [here (filter TYPEQU="F309")](https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip)
- (dataset 2) Education, file available [here](https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_enseignement_xy_csv.zip)

The extraction is performed directly from the online CSV files by a [Python script](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/code/Python/gf/bpe_extraction.py).

The list of columns extracted is given in the following table.

| Field name | Description | Data type | Data availability |
| --- | -- | --- |-------------------|
| AN | Reference year | Year (always '2020') | Datasets 1 & 2 |
| DEPCOM | Municipality | Code list | Datasets 1 & 2 |
| LAMBERT_X | Latitude | Float | Datasets 1 & 2 |
| LAMBERT_Y | Longitude | Float | Datasets 1 & 2 |
| QUALITE_XY | Quality of geogoding | Code list | Datasets 1 & 2 |
| TYPEQU | Type of facility | Code list | Datasets 1 & 2 |
| CL_PELEM | Presence or absence of a pre-elementary class in primary schools | Code list | Datasets 2 |
| CL_PGE | Presence or absence of a preparatory class for the high schools in upper secondary | Code list | Datasets 2 |
| EP | Membership or not in a priority education scheme | Code list | Datasets 2 |
| SECT | Membership of the public or private education sector | Code list | Datasets 2 |

Geographic coordinates are expressed using the [Lambert](https://en.wikipedia.org/wiki/Lambert_conformal_conic_projection) [93](https://spatialreference.org/ref/epsg/rgf93-lambert-93/) coordinate system.


In DDI-CDI terms, the BPE data corresponds to a "Wide" data structure.
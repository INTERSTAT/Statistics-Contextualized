# Geolocalized Facilities (GF) Interstat pilot

## Data

The central source of data for this pilot is the Permanent database of facilities ([BPE](https://www.insee.fr/en/metadonnees/source/serie/s1161) in French) published by Insee. For a working example, we extract a list of columns from the CSV file containing the data from the 2020 edition of the database.

BPE data is available in CSV and Excel formats from the BPE [landing page](https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656). More specifically, the example uses an extract of the geocoded "sport & leisure" BPE data. The extraction is performed directly from the online CSV files by an [R script](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/code/R/bpe-extraction.R).

The list of columns extracted is given in the following table.

| Field name | Description | Data type |
| --- | --- | --- |
| AN | Reference year | Year (always '2020') |
| COUVERT | Roof indicator | Code list |
| DEPCOM | Municipality | Code list |
| ECLAIRE | Light indicator | Code list |
| LAMBERT_X | Latitude | Float |
| LAMBERT_Y | Longitude | Float |
| NBSALLES | Number of rooms | Integer |
| QUALITE_XY | Quality of geogoding | Code list |
| TYPEQU | Type of facility | Code list |

Geographic coordinates are expressed using the [Lambert](https://en.wikipedia.org/wiki/Lambert_conformal_conic_projection) [93](https://spatialreference.org/ref/epsg/rgf93-lambert-93/) coordinate system.

In DDI-CDI terms, the BPE data corresponds to a "Wide" data structure.
# Data for the study on DDI-CDI/NGSI-LD interoperability


## Population be sex, age and geographic local administrative unit

### CSV format

We use [CSV on the Web](https://www.w3.org/TR/tabular-data-primer/) in order to document the CSV data. The CSVW metadata are available [here](population-sample.csv-metadata.json).

For France, the data is taken from https://www.insee.fr/fr/statistiques/5395878?sommaire=5395927. The reference year is 2018 for the population counts and 2020 for the reference geography. An [R script](code/R/french-population-age-distribution.R) allows to obtain the CSV file directly from the data published on Insee's web site.
# Data for the study on DDI-CDI/NGSI-LD interoperability


## Population be sex, age and geographic local administrative unit

### CSV format

We use [CSV on the Web](https://www.w3.org/TR/tabular-data-primer/) in order to document the CSV data. The CSVW metadata are available [here](population-sample.csv-metadata.json).

For France, the data is taken from https://www.insee.fr/fr/statistiques/5395878?sommaire=5395927. The reference year is 2018 for the population counts and 2020 for the reference geography. An [R script](code/R/french-population-age-distribution.R) allows to obtain the CSV file directly from the data published on Insee's web site. The script uses auxiliary CSV files containing reference data about [age groups](age-groups.csv) and French [LAU/NUTS](nuts3.csv) which are also described in the CSVW metadata.

Below are the first lines of the CSV file to illustrate the structure of the data:

```
lau;nuts3;sex;age;population
01001;FRK21;1;Y_LT5;20,7279477469
01001;FRK21;1;Y5-9;21,7541546340
01001;FRK21;1;Y10-14;40,2451849698
01001;FRK21;1;Y15-19;28,7876046394
01001;FRK21;1;Y20-24;11,0446211444
01001;FRK21;1;Y25-29;15,1299023662
01001;FRK21;1;Y30-34;18,1519022694
01001;FRK21;1;Y35-39;17,8491155030
01001;FRK21;1;Y40-44;28,6834019797
```
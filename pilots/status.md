# Status of pilots

## SEP

### Data pipelines

#### Census data

* Models and metadata
  * Defined and documented

* French data
  * pipeline operational
  * completely automated
  * documented

* Italian data
  * pipeline operational
  * partly automated
  * manual part documentation issue 9 https://github.com/INTERSTAT/Statistics-Contextualized/issues/9#issuecomment-968995758

#### Air quality data

* Models and metadata
  * ontology to be updated, documentation in issue 21. Further documentation is to be updated shortly. 
  * connection to smart model IS defined, as the ontology concepts come from Air Quality Model (EEA) but it needs further revision to include meta ontologies
  * metadata are defined and codelists are taken from EEA and collected in tables on MySQL

* Data (French and Italian)
  * pipeline partly operational
  * extraction not automated
  * transform implemented via SQL
  * use of Nominatis API problematic (bad or absent post code, API usage policy limitative)
  * target RDF model is being implemented

## GF

* Models and metadata
  * updated version of [DDI-CDI RDF serialization for the Interstat GF pilot](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/gf-cdi.ttl)
  * target RDF model defined
  * CSVW specification automated for French data, metadata are expressed in French
  * First version of DCAT description created


* French data (Geolocalized Facilities 2020 for venues of exhibition and heritage & education)
  * pipeline operational
  * extraction automated
  * upload to GraphDB automated



* Italian data
  * data on schools extraction operational
  * alignment with data model in progress in progress (missing LAU)
  * first steps for extraction of museum data and cultural events


## S4Y

* Models and metadata
  * list of variables has been identified [here](https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1071249281)
  * metadata model is defined in [Issue 14](https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1095203474) 
  * code lists are defined in [Issue 14](https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1095203474)
   * ISCED, Institution type are defined in the issue and loaded in the MySQL repository
   * codelist like sex and age class can be inherited from census if needed

* French data
  * pipeline partly operational 
  * extraction automated
  * transform partly operational (retrieving "nuts3" and "sex" variables in progress)
  * target RDF model to define?

* Italian data
  * pipeline partly implemented (student attainment harmonization in relation to the common data model and ontology mapping to be completed) [Issue 14](https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1095203474)
  

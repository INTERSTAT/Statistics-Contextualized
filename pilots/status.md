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
  * manual part needs documentation

#### Air quality data

* Models and metadata
  * ontology defined, needs documentation
  * connection to smart model not defined
  * metadata not defined

* Data (French and Italian)
  * pipeline partly operational
  * extraction automated
  * transform / load to implement
  * use of Nominatis API problematic (bad or absent post code, API usage policy limitative)
  * target RDF model to define

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
  * no defined metadata model yet
  * code lists to define (sex and institution_type variables)

* French data
  * pipeline partly operational
  * extraction automated
  * transform partly operational (retrieving "nuts3" and "sex" variables in progress)
  * target RDF model to define?

* Italian data
  * pipeline not implemented. First step is to have a look at italian [datasets](https://github.com/INTERSTAT/Statistics-Contextualized/issues/14#issuecomment-1013005178) to get the same list of variables

# Test data for SDMX to NGSI-LD converter

Different data structure definitions and corresponding data sets are provided in order to test the SDMX to NGSI-LD converter. These test data are taken from two statistical domains:

* Capacities of tourist accomodations: number of accommodations, of bedrooms and of bed places from 2014 to 2022 for French NUTS3 areas
* National accounts: data about GDP and its main components from 2012 to 2020 for a subset of UE countries.

They are published on the project's GraphDB triple store in repository `conversion-test` and partitioned into the following graphs.

#### `<http://rdf.interstat.eng.it/graphs/structures/accounts>`

This graph contains a data structure definition with its components and code lists for the "national accounts" domain. The DSD groups 15 dimensions, 14 of which (all excepts `sdmx-dimension:timePeriod`) are grouped in a slice for modelling time series, one measure `sdmx-measure:obsValue`, and 25 attributes. The DSD is derived from the SDMX NA_MAIN DSD, using when possible the [SDMX RDF components](https://github.com/UKGovLD/publishing-statistical-data/tree/master/specs/src/main/vocab) defined in the RDF Data Cube Vocabulary recommandation.
	
#### `<http://rdf.interstat.eng.it/graphs/structures/tourism>`

This graph contains two data structure definitions with their components and code lists for the "tourism" domain. The first DSD contains 4 dimensions, two measures and two attributes. It uses the multi-measure pattern as described in the Data Cube specification and compatible with version 3.0 of SDMX. The second DSD use the "measure dimension" pattern, compatible with SDMX 2.1. It groups uses the same dimensions plus the measure dimension, 3 measures and 2 attributes.

#### `<http://rdf.interstat.eng.it/graphs/datasets/accounts>` and `<http://rdf.interstat.eng.it/graphs/datasets/accounts-slice>`

These graphs contain two datasets using the DSD on national accounts described above. The dataset with id `ds1003` contained in graph `<http://rdf.interstat.eng.it/graphs/datasets/accounts-slice>` is organized by slice, whereas dataset with id `ds1002` in graph `<http://rdf.interstat.eng.it/graphs/datasets/accounts>` is not.


#### `<http://rdf.interstat.eng.it/graphs/datasets/tourism>` and `<http://rdf.interstat.eng.it/graphs/datasets/tourism-multi>`

These graphs contain two datasets using the DSDs on tourism described above. The dataset with id `ds1000` contained in graph `<http://rdf.interstat.eng.it/graphs/datasets/tourism>` uses the DSD containing a measure dimension, whereas the dataset with id `ds1001` contained in graph `<http://rdf.interstat.eng.it/graphs/datasets/tourism-multi>` conforms to the DSD using multiple measures.

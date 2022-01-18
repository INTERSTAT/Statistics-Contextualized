# Support for Environment Policies (SEP) Interstat pilot

## Data

This pilot uses a combination of:

* air quality data (measures of air pollutants concentation by sensors);
* statistical census data.

### Air quality data

Air quality data is available from the European Environment Agency (EEA) at the [Air Quality e-Reporting](https://www.eea.europa.eu/data-and-maps/data/aqereporting-8) web page. More precisely, the "AIDE F" data flow seems in first approach to be the most relevant for the SEP pilot. The data corresponding to this flow can be General information about the Air Quality e-Reporting products is available in [this document](https://ftp.eea.europa.eu/www/aqereporting-3/AQeReporting_products_2018_v1.pdf). In particular, the description of variables for AIDE F is reproduced below.

| Field name | Description | Data type |
| --- | --- | --- |
| Country Or Territory | Country or territory name | string |
| Reporting Year | Year for which primary data have been reported | numeric |
| Namespace | Inspire identifier/namespace of reporting entity, given by data provider | string |
| Station LocalId | Inspire identifier (LocalId) of air quality measurement station, given by data provider | string |
| Sampling Point LocalId | Inspire identifier (LocalId) of sampling point, given by data provider | string |
| Sampling Point Latitude | Latitude of sampling point (decimal degrees) | numeric |
| Sampling Point Longitude | Longitude of sampling point (decimal degrees) | numeric |
| Pollutant | Air polluting substance, level of which is measured and reported to the EEA (see notation in [Data Dictionary](http://dd.eionet.europa.eu/vocabulary/aq/pollutant)) | string |
| Aggregation Type | Information about process of data aggregation into annual values (see in [Data Dictionary](http://dd.eionet.europa.eu/vocabulary/aq/aggregationprocess)) | string |
| AQ Value | Concentration or level of air polluting substance, here given as an aggregation of air pollutant concentration values from primary observation time series | numeric |
| Unit | Unit of concentration or level of air polluting substance (see in [Data Dictionary](http://dd.eionet.europa.eu/vocabulary/uom/concentration)) | string |
| Begin Position | Date time begin of measurement (time zone as defined for the air quality network) | datetime |
| End Position | Date time end of measurement (time zone as defined for the air quality network) | datetime |
| Validity | Validity flags based on Data Capture, data are 'not valid' if Data Capture <75% (see in [Data Dictionary](http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity)) | string |
| Verification | Information based on verification flags found in reported time series (see in [Data Dictionary](http://dd.eionet.europa.eu/vocabulary/aq/observationverification)) | string |
| Data Coverage | Proportion of valid measurement included in the aggregation process within averaging period, expressed as percentage. If Data Coverage < 75% for averaging period of a year, annual statistics should not be included in air quality assessments, if Data Coverage < 85% (in a year), annual statistics should not be included in compliance checks | numeric |
| Data Capture | Proportion of valid measurement time relative total measured time (time coverage) in averaging period, expressed as percentage | numeric |
| Time Coverage | Proportion of total measured time, calculated from start and end time of observation, within the full averaging period, expressed as percentage | numeric |
| Update Time | Time of the latest update of the calculated statistics | datetime |

The code lists used in the data are documented in the [Eionet](https://www.eionet.europa.eu/) [Data Dictionary](https://dd.eionet.europa.eu/). They are available in SKOS form, with additional information. For example the [AQD - Air Quality Pollutants](http://dd.eionet.europa.eu/vocabulary/aq/pollutant/) scheme contains also data on recommended unit or measurement equipment for the pollutant. Most URIs are dereferenceable, at least in a browser.

In DDI-CDI terms, air quality data from the AIDE F flow would be naturally represented as a "Wide" data structure.

### Census data

The SEP pilot plans to combine air quality data with demographic data from the French and Italian censuses. The precise choice of census data has to be agreed upon within the Interstat project, but it is likely that data whose metadata are defined by [European legislation](https://ec.europa.eu/eurostat/fr/web/population-demography/population-housing-censuses/legislation) will be selected in order to minimize interoperability questions and ensure reproductibility at the European level. The [explanatory notes](https://ec.europa.eu/eurostat/en/web/products-manuals-and-guidelines/-/ks-gq-18-010) for the 2021 census round give details on this subject. In particular, they present a new feature of the 2021 round: the dissemination of population data at the 1 km² grid level, for which Eurostat will provide Inspire metadata and which will be particularly interesting to combine with air quality data.

For testing purposes, it is easier to start with simple data, for example the breakdown of population by age range, sex and municipality.

In DDI-CDI terms, census data corresponds to a "Dimensional" (actually "Cube") data structure. The definition of this data structure according to the SDMX model is described [here](sep-dsd.md).
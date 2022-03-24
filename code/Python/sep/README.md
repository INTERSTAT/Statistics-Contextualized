# SEP

This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See description [here](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep).


## Air quality data

The SEP pilot use case uses data about air quality, and more precisely about concentration in the atmosphere of several pollutants. The pollutants selected are:

* Nitrogen dioxide
* Ozone
* Particulate matter 10
* Particulate matter 2.5

Different sources for the air quality data are used, detailed in the following sections.

### French data

The French data is queried from the API provided by the European Environment Agency. The variables extracted are: Country, StationID, Latitude, Longitude, AGType (aggregation type), AQValue (air quality value).

### Italian data

For Italy, the data is taken from the [Ispra website](https://annuario.isprambiente.it/).
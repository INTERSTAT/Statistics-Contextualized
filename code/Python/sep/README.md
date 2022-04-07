# SEP

This workflow implements the INTERSTAT Statistics contextualized SEP use case.

See description [here](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep).


## Air quality data

The SEP pilot use case uses data about air quality, and more precisely about concentration in the atmosphere of several pollutants. The pollutants selected are:

| Name                   | Id    |
|------------------------|-------|
| Nitrogen dioxide       | NO2   |
| Ozone                  | O3    |
| Particulate matter 10  | PM10  |
| Particulate matter 2.5 | PM2.5 |

Different sources for the air quality data are used, detailed in the following sections.

### French data

The French data is queried from the API provided by the European Environment Agency. The variables extracted are: `Country`, `StationID`, `Latitude`, `Longitude`, `AGType` (aggregation type), `AQValue` (air quality value). A query is made for each pollutant, and the results are concatenated with addition of two columns: `Pollutant`, containing the pollutant identifier (see table) and `ReportingYear`, which is constant and copied from the configuration file.

### Italian data

For Italy, the data is taken from the [Ispra website](https://annuario.isprambiente.it/). Ispra publishes data as Excel files that are different for each pollutant, and also have different structures. This is detailed in [issue 17](https://github.com/INTERSTAT/Statistics-Contextualized/issues/17). The variables extracted from the different Excel files or added are `Country`, `StationID`, `Municipality`, `LAU`, `AQValue`, `Pollutant` and `ReportingYear`.      
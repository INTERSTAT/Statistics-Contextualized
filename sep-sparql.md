# Examples of SPARQL queries for the SEP use case

## Queries on the census data

### Total of population by NUTS3 and sex

```
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#>
PREFIX isc: <http://id.cef-interstat.eu/sc/>

SELECT ?nuts3 ?sex (sum(?pop) AS ?population) WHERE {
    ?obs qb:dataSet isc:ds1 ;
         sdmx-measure:obsValue ?pop ;
         isc:dim-sex ?sex ;
         isc:att-nuts3 ?nuts3 .
}
GROUP BY ?nuts3 ?sex
ORDER BY ?nuts3 ?sex
```

# Data Structure Definitions for the study on DDI-CDI/NGSI-LD interoperability

## Introduction

The DDI-CDI/NGSI-LD [interoperability test](https://github.com/FranckCo/Statistics-Contextualized/blob/main/test-case-sep.md) uses data on air quality and census data. For the census data, we will use simple cubes defined using the SDMX data model and built on the harmonized definitions specified in the European legislation, precisely documented in the EU legislation on the 2021 population and housing censuses [explanatory notes](https://ec.europa.eu/eurostat/documents/3859598/9670557/KS-GQ-18-010-EN-N.pdf/c3df7fcb-f134-4398-94c8-4be0b7ec0494?t=1552653277000).

In order to minimize technical interoperability questions, we will directly express data and metadata as linked data using the W3C [Data Cube](https://www.w3.org/TR/vocab-data-cube/) Recommendation and the [SDMX Content-Oriented Guidelines](https://sdmx.org/?page_id=4345) components [translated in RDF](https://github.com/UKGovLD/publishing-statistical-data/tree/master/specs/src/main/vocab) by the UK Government Linked Data Working Group.

The URIs of the ressources will be taken in the `http://id.cef-interstat.eu/sc/` namespace (where 'sc' stands for 'statistics contextualized').

## Population be sex, age and geographic local administrative unit

### Cube structure

This data cube will have 3 dimensions: sex, age groups and [LAU](https://ec.europa.eu/eurostat/web/nuts/local-administrative-units) (corresponding to communes in France and comuni in Italy), considered as a geographic dimension.

The construction of the DSD is detailed below; the complete DSD is available as a [Turtle file](sep-dsd-1.ttl).

### Dimensions

Three components are attached to the DSD to represent the three cube dimensions.

Regarding the age, the reference code list is CL_AGE, produced by Eurostat and currently in version 5.0 (`urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_AGE(5.0)`), available from the [EURO SDMX Registry](https://webgate.ec.europa.eu/sdmxregistry/) and described in [Regulation 2017/543](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0543&from=EN). CL_AGE actually combines 3 code lists: AGE.L is flat and contains broad age groups, AGE.M adds a second level with 5-year age groups, and AGE.H adds a third level with categories for each single age in years. For our needs, the second level of AGE.M is enough. For simplicity, we can derive from CL_AGE a SKOS concept scheme containing only the second-level codes of AGE.M. The corresponding dimension can then be defined:

```
<http://id.cef-interstat.eu/sc/dim-age>
    a             qb:CodedProperty , qb:DimensionProperty ;
    rdfs:label    "Five-year age group"@en , "Âge quinquennal"@fr ;
    rdfs:range    <http://id.cef-interstat.eu/sc/age-m> ;
    qb:codeList   <http://id.cef-interstat.eu/sc/cl-age-m> ;
    qb:concept    sdmx-concept:age .
```

The 'sex' dimension uses the CL_SEX code list. Several versions are available, but the Census Hub uses version 1.0 (`urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_SEX(1.0)`). There again, we can create a corresponding SKOS concept scheme and use to define the dimension:

```
<http://id.cef-interstat.eu/sc/dim-sex>
    a             qb:CodedProperty , qb:DimensionProperty ;
    rdfs:label    "Sex"@en , "Sexe"@fr ;
    rdfs:range    <http://id.cef-interstat.eu/sc/sex> ;
    qb:codeList   <http://id.cef-interstat.eu/sc/cl-sex> ;
    qb:concept    sdmx-concept:sex .
```

For the geographic dimension, the relevant code list is GEO.H, which corresponds to the LAU level. For the 2021 Census Hub, the code list is associated to a specific 'GEO' concept (`urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept=ESTAT:CENSUSHUB_CONCEPTS_2021(1.0).GEO`), but for simplicity we will use the global SDMX REF_AREA concept. Here again, a SKOS concept scheme will be created from the list of French communes and Italian comuni.

```
<http://id.cef-interstat.eu/sc/dim-lau>
    a             qb:CodedProperty , qb:DimensionProperty ;
    rdfs:label    "Local Administrative Unit"@en , "Unité Administrative Locale"@fr ;
    rdfs:range    <http://id.cef-interstat.eu/sc/lau> ;
    qb:codeList   <http://id.cef-interstat.eu/sc/cl-lau> ;
    qb:concept    sdmx-concept:refArea .
```

### Attributes and measure

An attribute, corresponding to the SDMX UNIT_MEASURE concept, can be attached to the Data Structure Definition (DSD) in order to specify that population counts are expressed in number of persons. To express the value of the attribute, we can use the "Persons" value in the [Eurostat SDMX CL_UNIT](https://registry.sdmx.org/ws/public/sdmxapi/rest/codelist/ESTAT/CL_UNIT/1.2) code list, which has `urn:sdmx:org.sdmx.infomodel.codelist.Code=ESTAT:CL_UNIT(1.2).PS` for URI.

We can also define attributes to represent geographic levels above the LAU in order to be able to aggregate data at NUTS 3 or NUTS 2 level. Such attributes would be attached at the observation level. For example:

```
<http://id.cef-interstat.eu/sc/att-nuts3>
    a             qb:CodedProperty , qb:AttributeProperty ;
    rdfs:label   "NUTS 3"@en , "NUTS 3"@fr ;
    rdfs:range   <http://id.cef-interstat.eu/sc/nuts3> ;
    qb:codeList  <http://id.cef-interstat.eu/sc/cl-nuts3> ;
    qb:concept   sdmx-concept:refArea .
```

Finally, for the measure, we can use the base SDMX OBS_VALUE concept.

### Data Structure Definition

Adding the component specifications for the dimensions, attributes and measure to the DSD, we have:

```
<http://id.cef-interstat.eu/sc/dsd1>
    a             qb:DataStructureDefinition ;
    rdfs:label    "Population by sex, age and local administrative unit"@en , "Population par sexe, âge et unité administrative locale"@fr ;
    qb:component  [ a                       qb:ComponentSpecification ;
                    qb:attribute            sdmx-attribute:unitMeasure ;
                    qb:componentAttachment  qb:DataSet
                  ] ;
    qb:component  [ a                       qb:ComponentSpecification ;
                    qb:attribute            <http://id.cef-interstat.eu/sc/att-nuts3> ;
                    qb:componentAttachment  qb:Observation
                  ] ;
    qb:component  [ a            qb:ComponentSpecification ;
                    qb:dimension <http://id.cef-interstat.eu/sc/dim-age>
                  ] ;
    qb:component  [ a             qb:ComponentSpecification ;
                    qb:dimension  <http://id.cef-interstat.eu/sc/dim-sex>
                   ] ;
    qb:component  [ a             qb:ComponentSpecification ;
                    qb:dimension  <http://id.cef-interstat.eu/sc/dim-lau>
                   ] ;
    qb:component  [ a             qb:ComponentSpecification ;
                    qb:measure  sdmx-measure:obsValue
                   ] .
```

### Dataset

With the previous specifications, the data set could be expressed as follows (observation values are fictitious):

```
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix qb:    <http://purl.org/linked-data/cube#> .
@prefix sdmx-concept: <http://purl.org/linked-data/sdmx/2009/concept#> .
@prefix sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#> .
@prefix sdmx-measure:    <http://purl.org/linked-data/sdmx/2009/measure#> .
@prefix isc: <http://id.cef-interstat.eu/sc/> .

isc:ds1 a qb:DataSet ;
    qb:structure isc:dsd1 ;
    rdfs:label "Population 15 and over by sex, age and activity status"@en , "Population de 15 ans ou plus par sexe, âge et type d'activité"@fr ;
    sdmx-attribute:unitMeasure <urn:sdmx:org.sdmx.infomodel.codelist.Code=ESTAT:CL_UNIT(1.2).PS> .

isc:obs-Y15-19-1-01001 a qb:Observation ;
    qb:dataSet isc:ds1 ;
    isc:dim-age isc:age-Y15-19;
    isc:dim-sex isc:sex-1 ;
    isc:dim-lau isc:lau-01001 ;
    isc:att-nuts3 isc:nuts3-FRK21 ;
    sdmx-measure:obsValue "116.3"^^xsd:float .

...

isc:obs-Y15-19-1-001001 a qb:Observation ;
    qb:dataSet isc:ds1 ;
    isc:dim-age isc:age-Y15-19;
    isc:dim-sex isc:sex-1 ;
    isc:dim-lau isc:lau-001001 ;
    isc:att-nuts3 isc:nuts3-ITC11 ;
    sdmx-measure:obsValue "231.4"^^xsd:float .

...
```

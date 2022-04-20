# Geolocalized Facilities (GF) Interstat pilot

## Data

### French data

The central source of French data for this pilot is the Permanent database of facilities ([BPE](https://www.insee.fr/en/metadonnees/source/serie/s1161) in French) published by Insee. For a working example, we extract a list of columns from the CSV file containing the data from the 2020 edition of the database.

BPE data and metatadata are available in CSV formats from the BPE [landing page](https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656). More specifically, the example uses an extract of the following geocoded facilities:
- (dataset 1) Exposition venues and heritage, file available [here (filter TYPEQU="F309")](https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_sport_Loisir_xy_csv.zip)
- (dataset 2) Education, file available [here](https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_enseignement_xy_csv.zip)

The extraction is performed directly from the online CSV files by a [Python script](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/code/Python/gf/bpe_extraction.py).

The list of columns extracted is given in the following table.

| Field name | Description | Data type | Data availability |
| --- | -- | --- |-------------------|
| Facility_ID | Facility identifier | String | Datasets 1 & 2 |
| Year | Reference year | Year (always '2020') | Datasets 1 & 2 |
| LAU | Municipality | Code list | Datasets 1 & 2 |
| Lambert_X | Latitude | Float | Datasets 1 & 2 |
| Lambert_Y | Longitude | Float | Datasets 1 & 2 |
| Quality_XY | Quality of geogoding | Code list | Datasets 1 & 2 |
| FacilityType | Type of facility | Code list | Datasets 1 & 2 |
| CL_PELEM | Presence or absence of a pre-elementary class in primary schools | Code list | Datasets 2 |
| CL_PGE | Presence or absence of a preparatory class for the high schools in upper secondary | Code list | Datasets 2 |
| EP | Membership or not in a priority education scheme | Code list | Datasets 2 |
| Sector | Membership of the public or private education sector | Code list | Datasets 2 |

French geographic coordinates are expressed using the [Lambert](https://en.wikipedia.org/wiki/Lambert_conformal_conic_projection) [93](https://spatialreference.org/ref/epsg/rgf93-lambert-93/) coordinate system.


In DDI-CDI terms, the BPE data corresponds to a "wide" data structure. A tentative [DDI-CDI description](gf-cdi.ttl) of the BPE file is provided. A [CSV on the web description](https://interstat.eng.it/files/gf/output/gf_data_fr.csv-metadata.json) is also available.

### Italian data

(TODO)

## Model

The target model for the data on facilities is [expressed in OWL](https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/gf-ontology.ttl) (see also [WebVOWL visualization](https://service.tib.eu/webvowl/#iri=https://raw.githubusercontent.com/INTERSTAT/Statistics-Contextualized/main/pilots/gf/gf-ontology.ttl)). The overall structure of the ontology is represented in the following figure:

![GF ontology](../../gf-ontology.png)

The facility coordinates are represented using the [GeoSPARQL](https://www.ogc.org/standards/geosparql) ontology. In the BPE, the quality of the geocoding is documented according to a 3-star-like system. This is rendered in RDF using quality annotations defined in the [DQV vocabulary](https://www.w3.org/TR/vocab-dqv/). The articulation of these different elements is shown in the following figure.

![GF quality](../../gf-quality.png)

An example of corresponding code is given below (prefix declarations are omitted):

```
    <http://id.cef-interstat.eu/sc/gf/facility/AJFQKT500> a igf:Facility ;
        rdfs:label "Lycée Frédéric Mistral"@en ;    
        dc:identifier "AJFQKT500" ;
        dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/C501> ;
        geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/1> .

    <http://id.cef-interstat.eu/sc/gf/geometry/AJFQKT500> a geo:Geometry ;
        rdfs:label "Localization of Lycée Frédéric Mistral" ;
        geo:asWKT "POINT(841092.05,6545270.87)"^^geo:wktLiteral .

    <http://id.cef-interstat.eu/sc/gf/quality/AJFQKT500> a dqv:QualityAnnotation ;
        oa:hasBody <http://id.insee.fr/interstat/gf/QualityLevel/GOOD> ;
        oa:hasTarget <http://id.cef-interstat.eu/sc/gf/geometry/AJFQKT500> .

```
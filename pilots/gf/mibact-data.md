# Example of MIBACT data

Here are examples of SPARQL DESCRIBE queries and corresponding Turtle results. Queries are executed on the "Dati Cultura" [SPARQL endpoint](https://dati.cultura.gov.it/sparql). Results are limited to the statements of which the resource is subject.

## Musea

The following queries return information on one given museum and some linked resources. The following diagram represents the associations between the different individuals.

```mermaid
  graph LR;
      M([museum])-- hasSite -->S([site]);
      S-- siteAddress -->A([adress]);
      S-- hasGeometry -->G([geometry]);
	  A-- hasCity -->C([city]);
```


### Museum

#### Query

```
DESCRIBE <http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/100000>
```

#### Results

```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix cis: <http://dati.beniculturali.it/cis/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns3: <http://dati.beniculturali.it/mibact/luoghi/resource/Site/> .
@prefix ns4: <http://dati.beniculturali.it/mibact/luoghi/resource/SubjectDiscipline/> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix clvapit: <https://w3id.org/italia/onto/CLV/> .
@prefix ns9: <http://dati.beniculturali.it/mibact/luoghi/resource/Geometry/> .
@prefix l0: <https://w3id.org/italia/onto/l0/> .
@prefix accessCondition: <https://w3id.org/italia/onto/AccessCondition/> .
@prefix ns12: <http://dati.beniculturali.it/mibact/luoghi/resource/OpeningHoursSpecification/> .
@prefix ns13: <http://dati.beniculturali.it/mibact/luoghi/resource/Booking/> .
@prefix smapit: <https://w3id.org/italia/onto/SM/> .
@prefix ns15: <http://dati.beniculturali.it/mibact/luoghi/resource/OnlineContactPoint/> .
@prefix roapit: <https://w3id.org/italia/onto/RO/> .
@prefix ns17: <http://dati.beniculturali.it/mibact/luoghi/resource/RoleInTime/> .

<http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/100000> rdf:type cis:CulturalInstituteOrSite ;
    rdfs:label "Museo civico aufidenate \"Antonio De Nino\""@it ;
    cis:hasSite ns3:Sede_di_100000 ;
    cis:hasDiscipline ns4:Contenuti_Editoriali ;
    geo:lat "41.734238" ;
    geo:long "14.032534" ;
    foaf:depiction <http://media.beniculturali.it/mibac/files/boards/388a5474724a15af0ace7a40ab3301de/museo%20civico2.JPG> ;
    dc:type "Museo, Galleria e/o raccolta" ;
    clvapit:hasGeometry ns9:Coordinate_geografiche_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000 ;
    l0:identifier "DBUnico.100000" ;
    cis:hasCISNameInTime <http://dati.beniculturali.it/mibact/luoghi/resource/CISNameInTime/100000> ;
    cis:institutionalCISName "Museo civico aufidenate \"Antonio De Nino\""@it ;
    accessCondition:hasAccessCondition ns12:Chiusura_100000 ;
    accessCondition:hasAccessCondition ns13:None ;
    smapit:hasOnlineContactPoint ns15:http___www_comune_alfedena_aq_it-protocollo_comune_alfedena_aq_it-0864_87114 ;
    l0:description "Il museo, fondato nel 1897, conserva i reperti pi\u00F9 importanti degli scavi effettuati nella necropoli sannita di Alfedena-Campo Consolino.\u00A0Le campagne di scavo, avviate da Lucio Mariani alla fine del XIX secolo, hanno portato alla luce sepolture a inumazione dal VI al IV secolo a.C. e ricchi corredi funerari; di particolare interesse un cinturone in bronzo, una corazza sannitica a tre dischi e due kardiophylakes."@it ;
    foaf:primaryTopic <http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/100000> ;
    ns17:_enteProprietario_100000 roapit:forEntity <http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/100000> ;
    ns17:Mibac_enteCompetenteTutela_100000 roapit:forEntity <http://dati.beniculturali.it/mibact/luoghi/resource/CulturalInstituteOrSite/100000> .
```

### Site

#### Query

```
DESCRIBE <http://dati.beniculturali.it/mibact/luoghi/resource/Site/Sede_di_100000>
```

#### Results

```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix ns1: <http://dati.beniculturali.it/mibact/luoghi/resource/Site/> .
@prefix cis: <http://dati.beniculturali.it/cis/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns4: <http://dati.beniculturali.it/mibact/luoghi/resource/Address/> .
@prefix clvapit: <https://w3id.org/italia/onto/CLV/> .
@prefix ns6: <http://dati.beniculturali.it/mibact/luoghi/resource/Geometry/> .
@prefix l0: <https://w3id.org/italia/onto/l0/> .

ns1:Sede_di_100000 rdf:type cis:Site 
    rdfs:label "Sede di Museo civico aufidenate \"Antonio De Nino\""@it .
    cis:siteAddress ns4:Indirizzo_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000 .
    clvapit:hasGeometry ns6:Coordinate_geografiche_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000 .
    l0:name "Sede di Museo civico aufidenate \"Antonio De Nino\""@it .
```

### Site address

#### Query

```
DESCRIBE <http://dati.beniculturali.it/mibact/luoghi/resource/Address/Indirizzo_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000>
```

#### Results

```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns1: <http://dati.beniculturali.it/mibact/luoghi/resource/Address/> .
@prefix ns4: <http://dati.beniculturali.it/mibact/luoghi/resource/Province/> .
@prefix clvapit: <https://w3id.org/italia/onto/CLV/> .
@prefix ns5: <http://dati.beniculturali.it/mibact/luoghi/resource/Region/> .
@prefix ns6: <http://dati.beniculturali.it/mibact/luoghi/resource/Country/> .
@prefix ns7: <http://dati.beniculturali.it/mibact/luoghi/resource/City/> .

ns1:Indirizzo_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000 rdf:type clvapit:Address .
    rdfs:label "Indirizzo della Sede di: Museo civico aufidenate \"Antonio De Nino\""@it .
    clvapit:hasProvince ns4:L_Aquila .
    clvapit:hasRegion ns5:Abruzzo ;
    clvapit:fullAddress "Viale Mansueto De Amicis - Alfedena" .
    clvapit:hasCountry ns6:Italia ;
    clvapit:postCode "67030" .
    clvapit:hasCity ns7:Alfedena ;
    clvapit:hasStreetToponym <http://dati.beniculturali.it/mibact/luoghi/resource/StreetToponym/100000> .
```

### Site geometry

#### Query

```
DESCRIBE <http://dati.beniculturali.it/mibact/luoghi/resource/Geometry/Coordinate_geografiche_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000>
```

#### Results

```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns1: <http://dati.beniculturali.it/mibact/luoghi/resource/Geometry/> .
@prefix clvapit: <https://w3id.org/italia/onto/CLV/> .
@prefix ns4: <http://dati.beniculturali.it/mibact/luoghi/resource/GeometryType/> .
@prefix ns5: <http://dati.beniculturali.it/mibact/luoghi/resource/Site/> .

ns1:Coordinate_geografiche_della_sede_di_Museo_civico_aufidenate__Antonio_De_Nino__100000 rdf:type clvapit:Geometry .
    rdfs:label "Coordinate geografiche della Sede di: Museo civico aufidenate \"Antonio De Nino\""@it .
    clvapit:hasGeometryType ns4:Point ;
    clvapit:lat "41.734238" ;
    clvapit:long "14.032534" .
```


### City

#### Query

```
DESCRIBE <http://dati.beniculturali.it/mibact/luoghi/resource/City/Alfedena>
```

#### Results

```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix clvapit: <https://w3id.org/italia/onto/CLV/> .
@prefix ns1: <http://dati.beniculturali.it/mibact/luoghi/resource/Address/> .
@prefix ns2: <http://dati.beniculturali.it/mibact/luoghi/resource/City/> .
@prefix ns4: <https://w3id.org/arco/resource/City/> .
@prefix ns5: <http://dati.beniculturali.it/iccd/fotografico/resource/City/> .
@prefix ns8: <http://dati.beniculturali.it/mibact/luoghi/resource/Province/> .
@prefix l0: <https://w3id.org/italia/onto/l0/> .

ns2:Alfedena rdf:type clvapit:City ,
    clvapit:Feature .
    rdfs:label "Alfedena" ;
    owl:sameAs ns4:alfedena , <http://dati.beniculturali.it/iccu/anagrafe/resource/City/066003> , ns5:alfedena .
    clvapit:hasHigherRank ns8:L_Aquila .
    l0:name "Alfedena" .
```
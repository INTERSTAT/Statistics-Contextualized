# Presentation at the SDMX Global Conference

## General information

The [8th SDMX Global Conference](https://en.www.inegi.org.mx/eventos/2021/sdmx/) will be held virtually during September 27–30, 2021, with the theme “Data without Barriers”. The INTERSTAT project submitted an abstract, which was accepted. The text of the submission is reproduced below.

According to the preliminary program communicated by the Organizing Committee, the talk will take place during Session V: “Using SDMX to Modernize Statistical Processes and IT Infrastructure”, in Breakout Room 2, on September 29 from 12:30 to 12:45 Central Time (19:30 - 19:45 CEST). Slides must be provided by Friday, August 27, and participants must register for the conference at https://www.cvent.com/d/1jqy10.

## Presentation outline

We should aim at a duration of 12 minutes, so about 10 slides. The public is mainly from the SDMX community (banking and statistics), and from all parts of the world, so they are probably not familiar with the CEF. DDI-CDI might be slightly better known, but not much. Thus, it is proposed to concentrate on interoperability of NGSI-LD with SDMX models, in particular the VTL data model which is closer to DDI-CDI.

The presentation outline could be:

- The INTERSTAT project (2 slides)
- The CEF and the Context Broker (2 slides)
- Smart Models and examples (2 slides)
- The NGSI-LD Information Model (1 slide)
- Problem statement (1 slide)
- First results (1 slide)
- Future work (1 slide)


## Submission

##### Title: SDMX towards context information: achieving interoperability with NGSI-LD

##### Presenters: Franck Cotton (Insee), Fernando Lopez (FIWARE Foundation), Martino Maggio (Engineering Ingegneria Informatica)

INTERSTAT, a project funded under the European Connecting Europe Facility (CEF) initiative [1], aims at developing an open framework (including software tools and common ontologies) that will allow the interoperability between national statistical portals and the European Data portal to build cross-border services based on these datasets.

One of the activities to reach this interoperability is to allow statistical open data to be made available through a key building block of the CEF infrastructure known as the Context Broker [2]. This would allow, for example, to disseminate statistical data in a way that can be both contextualized (e.g. in time and space), interoperable with other sources, statistical or otherwise, and available via simple and standard web services for consumption on various platforms, as well as connected with automatic tools for AI/ML analysis.

The core specification for the Context Broker is NGSI-LD [3], an ETSI standard which is also the de facto standard for context information (think IoT, Smart Cities, etc.). NGSI-LD is mainly an information model combined with an API. The information model consists in a simple cross-domain ontology which is based on a core metamodel (actually the "property graph" model) which is itself expressed as RDF/RDFS through a simple mapping and represented in JSON-LD. Domain-specific models can be built on these foundations. A very comprehensive ecosystem for building these domain-specific models is available: see [4]. This is a collaborative initiative impulsed by FIWARE Foundation, TMForum and IUDX (Indian Urban Data Exchange) initiative.

In order to disseminate statistical information through the Context Broker, it is necessary to map statistical business information models to NGSI-LD. The INTERSTAT project is studying how to achieve this objective: in particular mapping the SDMX information model, the VTL data model, other foundational data, or metadata models used in the statistical community, creating a “bridge” with NGSI-LD. The final outcomes of this activity will be, not only cross-standard data models, but also a concrete software tool that implements this bridge capability.

The INTERSTAT project includes three pilots that will allow to experiment and validated the results of this activity.

References:

[1] [Connecting Europe Facility](https://ec.europa.eu/inea/en/connecting-europe-facility).
[2] [CEF Context Broker](https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/Context+Broker).
[3] [NGSI-LD API](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.04.02_60/gs_CIM009v010402p.pdf).
[4] [Smart Data Models](https://smartdatamodels.org/).


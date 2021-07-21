# Resources and references

## DDI-CDI

* [Review page](https://ddi-alliance.atlassian.net/wiki/spaces/DDI4/pages/860815393/DDI+Cross+Domain+Integration+DDI-CDI+Review) on the DDI Alliance web site
* [Model](https://ddi-alliance.bitbucket.io/DDI-CDI/DDI-CDI_Public_Review_1/2_Model/DDI-CDI_PublicReviewRelease_1-0.eap) in [Enterprise Architect](https://sparxsystems.com/) format
* [UML diagrams](https://ddi-alliance.bitbucket.io/DDI-CDI/DDI-CDI_Public_Review_1/2_Model/Supporting_Documents/DDI-CDI_PublicReviewRelease_1-0_UMLDiagrams.pdf)
* [Field-level documentation](https://ddi-alliance.bitbucket.io/DDI-CDI/DDI-CDI_Public_Review_1/2_Model/Field-Level_Documentation/index.html)
* [Presentation](https://www.youtube.com/watch?v=UbAgPKz6PN0) at EDDI 2021

## NGSI-LD

* [ETSI page](https://www.etsi.org/committee/1422-cim) on context information management
* [NGSI-LD specification](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.04.02_60/gs_CIM009v010402p.pdf) (V1.4.2, April 2021)
The core specification for the Context Broker is NGSI-LD, an ETSI standard which is also the de facto standard for context information (IoT, Smart Cities, etc.). NGSI-LD is mainly an  information model combined with an API. The specification is available from https://www.etsi.org/committee/1422-cim, the latest version (last April) is V1.4.2, directly accessible at  https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.04.02_60/gs_CIM009v010402p.pdf. The information model consists in a simple cross-domain ontology which is based on a core metamodel (actually the "property graph" model) which is itself expressed as RDF/RDFS (see figure aattached). Domain-specific models can be built on these foundations. There is actually a very nice ecosystem for building these domain-specific models: see https://smartdatamodels.org/, https://github.com/smart-data-models and the recording of a recent webinar at https://www.youtube.com/watch?v=26i-DZVBgh8, especially the parts on data models and performance.

## Smart data models

### General information

* [Web site](https://smartdatamodels.org)
* [Twitter feed](https://twitter.com/smartdatamodels)
* [Webinar recording](https://www.youtube.com/watch?v=26i-DZVBgh8&t=2052s)

### Using the data models
* [Search page](https://smartdatamodels.org/index.php/ddbb-of-properties-descriptions/)
* [GitHub page](https://github.com/smart-data-models)
* [Generate a NGSI-LD](https://smartdatamodels.org/index.php/generate-a-ngsi-ld-payload-based-on-a-smart-data-model/)
* [Root for domains](https://github.com/smart-data-models/data-models/tree/master/specs)

### Contributing new data models

* [Draft a model](https://smartdatamodels.org/index.php/draft-a-data-model/)
* [Presentation for contributors](https://docs.google.com/presentation/d/e/2PACX-1vTs-Ng5dIAwkg91oTTUdt8ua7woBXhPnwavZ0FxgR8BsAI_Ek3C5q97Nd94HS8KhP-r_quD4H0fgyt3/pub?start=false&loop=false&delayms=3000#slide=id.p1) 
* [Contribution API](https://smartdatamodels.org/index.php/data-models-contribution-api/)
* [Validate a payload against a schema](https://smartdatamodels.org/index.php/check-a-schema-validates-a-payload/)
* [Create data model from a spreadsheet](https://smartdatamodels.org/index.php/create-data-model-from-your-google-spreadsheet/) without knowledge of JSON schema
* [Root for incubated datamodels](https://github.com/smart-data-models/incubated/tree/master)

# **DCAT-AP metadata for the description of the Census Dataset**

[**First version**]

The document contains a list of DCAT-AP metadata needed to describe the Census dataset. There are both mandatory ones according to the standard (DCAT-AP v1.2) and other useful recommended.

## Dataset: mandatory metadata

|  **Property**   |     **URI**     |  **Range**   |                                                               **Usage note**                                                                | **Card.** |
| :-------------: | :-------------: | :----------: | :-----------------------------------------------------------------------------------------------------------------------------------------: | :-------: |
|    **title**    |    dct:title    | rdfs:Literal |        This property contains a name given to the Dataset. This property can be repeated for parallel language versions of the name.        |   1..n    |
| **description** | dct:description | rdfs:Literal | This property contains a free-text account of the Dataset. This property can be repeated for parallel language versions of the description. |   1..n    |

## Dataset: recommended metadata

|       **Property**       |                          **URI**                           |     **Range**     |                                                                                                                           **Usage note**                                                                                                                           |     **Card.**      |
| :----------------------: | :--------------------------------------------------------: | :---------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----------------: |
|     **landing page**     |                      dcat:landingPage                      |   foaf:Document   | This property refers to a web page that provides access to the Dataset, its Distributions and/or additional information. It is intended to point to a landing page at the original data provider, not to a page on a site of a third party, such as an aggregator. |        0..n        |
|    **contact point**     |                     dcat:contactPoint                      |    vcard:Kind     |                                                                                This property contains contact information that can be used for sending comments about the Dataset.                                                                                 |        0..n        |
| **dataset distribution** |                     dcat:distribution                      | dcat:Distribution |                                                                                                   This property links the Dataset to an available Distribution.                                                                                                    |        0..n        |
|     **keyword/tag**      |                        dcat:keyword                        |   rdfs:Literal    |                                                                                                  This property contains a keyword or tag describing the Dataset.                                                                                                   |        0..n        |
|      **publisher**       |                       dct:publisher                        |    foaf:Agent     |                                                                                   This property refers to an entity (organisation) responsible for making the Dataset available.                                                                                   |        0..1        |
|    **theme/category**    | <p>dcat:theme,</p><p>subproperty of </p><p>dct:subject</p> |   skos:Concept    |                                                                                This property refers to a category of the Dataset. A Dataset may be associated with multiple themes.                                                                                | <p>0..n</p><p></p> |
|   **spatial coverage**   |                        dct:spatial                         |   dct:Location    |                                                                                            This property refers to a geographic region that is covered by the Dataset.                                                                                             |        0..n        |
|  **temporal coverage**   |                        dct:temporal                        | dct:PeriodOfTime  |                                                                                                 This property refers to a temporal period that the Dataset covers.                                                                                                 |        0..n        |

## Distribution: mandatory metadata

|  **Property**  |    **URI**     |   **Range**   |                                                                            **Usage note**                                                                             | **Card.** |
| :------------: | :------------: | :-----------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------: |
| **access URL** | dcat:accessURL | rdfs:Resource | This property contains a URL that gives access to a Distribution of the Dataset. The resource at the access URL may contain information about how to get the Dataset. |   1..n    |

## Distribution: recommended metadata

|   **Property**   |     **URI**      |       **Range**       |                                                                  **Usage note**                                                                  | **Card.** |
| :--------------: | :--------------: | :-------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------: | :-------: |
| **description**  | dct:description  |     rdfs:Literal      | This property contains a free-text account of the Distribution. This property can be repeated for parallel language versions of the description. |   0..n    |
|    **format**    |    dct:format    | dct:MediaTypeOrExtent |                                           This property refers to the file format of the Distribution.                                           |   0..1    |
| **download URL** | dcat:downloadURL |     rdfs:Resource     |                           This property contains a URL that is a direct link to a downloadable file in a given format.                           |   0..n    |
|   **licence**    |   dct:license    |  dct:LicenseDocument  |                               This property refers to the licence under which the Distribution is made available.                                |   0..1    |

## Namespaces

- **dcat:** <http://www.w3.org/ns/dcat>#
- **dct:** http://purl.org/dc/terms/
- **rdfs:** http://www.w3.org/2000/01/rdf-schema#
- **foaf:** http://xmlns.com/foaf/0.1/
- **vcard:** http://www.w3.org/2006/vcard/ns#
- **skos:** http://www.w3.org/2004/02/skos/core#

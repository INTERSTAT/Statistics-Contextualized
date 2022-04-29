# Deliverable: Milestone 6

## Introduction

### Scope and objectives of the document

This document describes the Interstat pilot services, how they were built and how they can be used. It is part of the Milestone 6 (M6) of the project, which consists in having the "pilot services deployed and working in real environments", and in particular in the availability of the pilot services applications. M6 pertains to Activity 3 of the project ("Pilot services execution and assessment"), which extends until the end of the project with additional milestones dedicated to the monitoring and assessment of the pilots. Therefore, the services and applications will continue to evolve by continuous improvement in the future. It was thus decided to keep this accompanying document relatively short and high-level and to reference where appropriate to the [online resources](https://github.com/INTERSTAT/), much more detailed and which will be kept up to date as the project cotinues to evolve.

The document starts with a short recap about the different pilots and the technical production environment set up for Interstat. General considerations on the development of pilots are then exposed, with a particular focus on the approaches followed for creating the data pipelines and on the technical stack used for the client applications. More detail is then provided for each of the three pilots, including a reminder of the business case, the description of the relevant models and of the data, metadata, pipeline process and client application. A summary of the lessons learned, the remaining problems and the next steps is given in conclusion.

*Should we say something about the difficulties due to Covid?*


### Short reminder about the pilots

* SEP (--> Istat)
* GF (--> Insee)
* S4Y (--> Istat)

## Reminder on the production environment

--> ENG

## Pilot development

In this section, we decribe how the pilot services were developed, with a specific focus on 

### Data pipelines

Two different approaches were used for the implementation of the data pipelines: a classical ETL ([Extract, transform, load](https://en.wikipedia.org/wiki/Extract,_transform,_load) pattern for the GF pilot, and an approach based on ontological aggregation for SEP and S4Y.

#### ETL approach

--> Insee

The GF ETL process was designed with the following principles in mind:

* openness
* maximal automation
* reproduciblity
* efficiency

Openness leads to developping all code on [GitHub](https://github.com/INTERSTAT/Statistics-Contextualized/tree/main/code/Python/gf) starting from the first line and to using only open source tools.

Maximal automation avoids manual treatments, which saves time and improves traceability. It is often a difficult principle to follow, in particular with messy data, since it requires rigour and a bigger development effort, but it largely pays off in the end, especially if source data changes frequently.

Reproducibility results from automation and from detailed documentation inside and outside code.

Efficiency is ensured by the choice of a technical framework that provides for execution of the pipeline in a distributed environment.

Regarding tooling, the following choices were made:

* use of [Python 3](https://www.python.org/) as a programming language
* use of [Prefect](https://www.prefect.io/) as a build, run, and monitor framework

Prefect allows for good modularity and readability of the code, and provides process visualisation tools for the conception and execution stages. Prefect pipelines can be executed locally, for example for test purposes, or on a [cloud platform](https://www.prefect.io/cloud/) (which can be installed on premises).

More details on the technical environment for the ETL Python implementation is available [here](https://interstat.github.io/Statistics-Contextualized/code/Python/).


#### Ontological approach

--> Istat

### Client applications

--> ENG

## Details by pilot

### Supporting environment policies (SEP)

--> Istat

#### Business case

Suggest to copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#support-for-environment-policies-sep

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

### Geolocalized facilities (GF)

--> Insee

#### Business case

The main objective of this pilot is to disseminate information about facilities or equipments so that it can be contextualized in space and integrated with other sources of data.

Two specific user stories are defined for the GF pilot:

* In the “visitor” case, we consider a user visiting a place she does not know and wondering where the nearest facilities of different types are located. She also would like to know what events are programmed  in  the  nearby  stadiums,  theatres  of  cultural  venues.  From  the  description  of locations or events, it should be simple to navigate on the web for further detail (e.g. on artists or sport teams, history of places, links to the locations’ web sites, etc.).

* The “local decider” story is about a person in charge of an investment decision at a local level. It can be the manager of a bus company wondering if he should replace an old vehicle, an employee of an educational public service assessing the creation of a new class in a community school, or a young couple thinking of moving to a rural place, etc. He needs information about the level and capacity of the equipment in the neighbourhood, linked with data on the demographic evolution at a fine level. He will probably need to combine that information with other sources more specifically relevant to his specific problem.

#### Models

Copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/test-case-gf.md#model

#### Data

Copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/test-case-gf.md#data

#### Metadata

Copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/test-case-gf.md#metadata

#### Process

Copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/test-case-gf.md#process

#### Client (--> ENG)

### The school for you (S4Y)

--> Istat

#### Business case

Suggest to copy/paste from https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/test-case.md#the-school-for-you-s4y

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

## Conclusions

### Lessons learned

* Most of the time on data cleaning (common finding)
* Some important data are still not easily accessible (-> link to EC data strategy, HVD...)
* Importance of metadata

### Remaining problems

* difficulties with the Context Broker (*do we want to mention that?*) 

### Next steps

* continuous improvement of pilots (document, automate, add sources, pimp client)
* assessment framework
* work on the context broker, especially at the model level (mention work on SDMX/NGSI-LD)
# Deliverable: Milestone 6

## Introduction

This document is part of the Milestone 6 (M6) of the Interstat project, which consists in having the "pilot services deployed and working in real environments", and in particular in the availability of the pilot services applications. M6 pertains to Activity 3 of the project ("Pilot services execution and assessment"), which extends until the end of the project with additional milestones dedicated to the monitoring and assessment of the pilots. Therefore, the services and applications will continue to evolve by continuous improvement in the future. It was thus decided to keep this accompanying document relatively short and high-level and to reference where appropriate to the [online resources](https://github.com/INTERSTAT/), much more detailed and which will be kept up to date as the project cotinues to evolve.

The document starts with a short recap about the different pilots and the technical production environment set up for Interstat. General considerations on the development of pilots are then exposed, with a particular focus on the approaches followed for creating the data pipelines and on the technical stack used for the client applications. More detail is then provided for each of the three pilots, including a reminder of the business case, the description of the relevant models and of the data, metadata, pipeline process and client application. A summary of the lessons learned, the remaining problems and the next steps is given in conclusion.

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

### Scope and objectives of deliverable

This short document describes the pilot services, how they were built and how they can be used.

### Short reminder of the pilots

* SEP (--> Istat)
* GF (--> Insee)
* S4Y (--> Istat)

## Reminder on the production environment

--> ENG

## Pilot development

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

### SEP

--> Istat

#### Business case

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

### GF

--> Insee

#### Business case

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

### S4Y

--> Istat

#### Business case

#### Models

#### Data

#### Metadata

#### Process

#### Client (--> ENG)

## Conclusions

### Lessons learned

### Remaining problems

* difficulties with the Context Broker (*do we want to mention that?*) 

### Next steps
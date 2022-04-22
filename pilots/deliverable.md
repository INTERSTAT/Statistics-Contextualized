# Deliverable

## Introduction

### Scope and objectives of deliverable

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

### Next steps
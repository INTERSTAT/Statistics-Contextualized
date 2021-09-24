# Problem statement

We want to publish statistical data with the Context Broker:

![Publish data with the Context Broker](img/ps-1.png)

But data means nothing without metadata, so we want also to publish metadata:

![Publish data and metadata with the Context Broker](img/ps-2.png)

Metadata comes in many flavors and many standards:

![Many types of metadata](img/ps-3.png)

For the sake of simplicity, we can start with structural metadata:

![Publish data and structural metadata with the Context Broker](img/ps-4.png)

We can also start with one specific kind of data, dimensional or cube data:

![Publish cube data and structural metadata with the Context Broker](img/ps-5.png)

If we shift to a model view, the question becomes interoperability of the SDMX Information Model (or its Data Cube transposition) with NGSI-LD:

![Transform SDMX-like data and structural metadata to NGSI-LD](img/ps-6.png)

But we should keep in mind that there are other kind of metadata:

![Transform SDMX-like data and metadata to NGSI-LD](img/ps-7.png)

And we should keep in mind that dimensional data is just one type of data, and there are other kinds that can for example be covered by CDI-DDI:

![Transform SDMX-like data and metadata to NGSI-LD](img/ps-8.png)
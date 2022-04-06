"""
Technical configuration for the GF pipeline.
"""

conf = {
    "flags": {
        "prefect": {
            "pushToCloudDashboard": False,
            "displayGraphviz": False
        },
        "flow": {
            "testing": True
        }
    },
    "env": {
        "workingDirectory": ""
    },
    "sparql": {
        "italianCulturalFacilities" : """
            select * {
                select distinct ?s as ?subject ?Nome_Istituzionale ?Descrizione
                ?Latitudine ?Longitudine
                ?Disciplina ?Indirizzo
                ?Codice_postale ?Comune ?Provincia ?WebSite {
                graph <http://dati.beniculturali.it/mibact/luoghi> {
                    ?s rdf:type cis:CulturalInstituteOrSite ;
                    cis:institutionalCISName ?Nome_Istituzionale .
                    optional { ?s l0:description ?Descrizione }
                    optional { ?s geo:lat ?Latitudine }
                    optional { ?s geo:long ?Longitudine }
                    optional { ?s cis:hasDiscipline [l0:name ?Disciplina] }
                    optional {
                    ?s cis:hasSite [cis:siteAddress ?address ] .
                    optional { ?address clvapit:fullAddress ?Indirizzo }
                    optional { ?address clvapit:postCode ?Codice_postale }
                    optional { ?address clvapit:hasCity [rdfs:label ?Comune] }
                    optional { ?address clvapit:hasProvince [rdfs:label ?Provincia] }
                    }
                    optional {
                    ?s smapit:hasOnlineContactPoint ?contactPoint . 
                    optional { ?contactPoint smapit:hasWebSite [smapit:URL ?WebSite] }    
                    }   
                }
                }
                order by ?s
            }
        """,
        "italianCulturalEvents": """
            prefix cis:<http://dati.beniculturali.it/cis/>
            prefix dc:<http://purl.org/dc/elements/1.1/>
            prefix l0:<https://w3id.org/italia/onto/l0/>
            prefix TI:<https://w3id.org/italia/onto/TI/>
            prefix SM:<https://w3id.org/italia/onto/SM/>
            prefix POT:<https://w3id.org/italia/onto/POT/>
            prefix CLV:<https://w3id.org/italia/onto/CLV/>
            prefix geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
            prefix foaf:<http://xmlns.com/foaf/0.1/>

            select distinct (?s as ?EVENTO) ?NOME
            (str(?DATA_INIZIO_EVENTO) as ?DATA_INIZIO_EVENTO)
            (str(?DATA_FINE_EVENTO) as ?DATA_FINE_EVENTO)
            ?CATEGORIA ?SITO_WEB ?EMAIL
            ?VIA ?NUMERO_CIVICO ?CAP ?COMUNE ?PROVINCIA ?REGIONE
            ?LATITUDINE ?LONGITUDINE
            {
            ?s a cis:CulturalEvent optional 
            { ?s dc:type ?CATEGORIA } optional 
            { ?s l0:name ?NOME } optional 
            { ?s TI:atTime/TI:startTime ?DATA_INIZIO_EVENTO } optional  
            { ?s TI:atTime/TI:endTime ?DATA_FINE_EVENTO } optional  
            { ?s SM:hasOnlineContactPoint ?cp1 filter (!contains(str(?cp1),"Biglietteria") && !contains(str(?cp1),"Prenotazioni")) optional
            { ?cp1 SM:hasWebSite/SM:URL ?SITO_WEB } optional  
            { ?cp1 SM:hasEmail/SM:emailAddress ?EMAIL }} optional  
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:hasStreetToponym/CLV:officialStreetName ?VIA } optional 
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:hasNumber/CLV:streetNumber ?NUMERO_CIVICO } optional  
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:postCode ?CAP } optional  
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:hasCity/l0:name ?COMUNE } optional  
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:hasProvince/l0:name ?PROVINCIA } optional  
            { ?s cis:isHostedBySite/cis:siteAddress/CLV:hasRegion/l0:name ?REGIONE } optional  
            { ?s geo:lat ?LATITUDINE } optional  
            { ?s geo:long ?LONGITUDINE } optional
            { ?s foaf:depiction ?IMMAGINE }
            }
        """
    }
}

"""
Helping functions for producing RDF triples
"""

# Lang tags
lang_en = "@en"
lang_fr = "@fr"
lang_it = "@it"

# Educational sector URI
sectors_uri = {"PU": "<http://id.insee.fr/interstat/gf/sector/public>", "PR": "<http://id.insee.fr/interstat/gf/sector/private>"}

def gen_rdf_facility(id, equipment_type, sector, lau, lang_tag=lang_en):
    # Handling facility subtype
    subtype = "igf:EducationFacility" if equipment_type[0] == "C" else "igf:SportLeisureFacility"
    # Producing sector prop
    sector_prop = f"igf:sector {sectors_uri[sector]} ;" if str(sector) != "nan" else ""
    
    return f"""
    <http://id.cef-interstat.eu/sc/gf/facility/{id}> a igf:Facility ;
        a {subtype} ;
        rdfs:label "Facility number {id}"{lang_tag} ;    
        dc:identifier "{id}" ;
        dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}> ;
        geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/{id}> ;
        {sector_prop}
        igf:inLAU "{lau}"^^xsd:token .
    """


def gen_rdf_geometry(id, x, y, lang_tag=lang_en):
    # Handling missing coordinates
    if str(x) == "nan" or str(y) == "nan":
        return ""
    return f"""
    <http://id.cef-interstat.eu/sc/gf/geometry/{id}> a geo:Geometry ;
        rdfs:label "Geometry for facility {id}"{lang_tag} ;
        geo:asWKT "POINT({x},{y})"^^geo:wktLiteral .
    """


def gen_rdf_quality(id, quality):
    return f"""
    <http://id.cef-interstat.eu/sc/gf/quality/{id}> a dqv:QualityAnnotation ;
        oa:hasBody <http://id.insee.fr/interstat/gf/QualityLevel/{quality}> ;
        oa:hasTarget <http://id.cef-interstat.eu/sc/gf/geometry/{id}> .
    """

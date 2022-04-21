"""
Helping functions for producing RDF triples
"""

# Lang tags
lang_en = "@en"
lang_fr = "@fr"
lang_it = "@it"

def gen_rdf_facility(id, equipment_type, lang_tag=lang_en):
    return f"""
    <http://id.cef-interstat.eu/sc/gf/facility/{id}> a igf:Facility ;
        rdfs:label "Facility number {id}"{lang_tag} ;    
        dc:identifier "{id}" ;
        dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}> ;
        geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/{id}> .
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

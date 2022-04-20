"""
Helping functions for producing RDF triples
"""

def gen_rdf_facility(id, equipment_type):
    return f"""
    <http://id.cef-interstat.eu/sc/gf/facility/{id}> a igf:Facility ;
        rdfs:label "Facility number {id}"@en ;    
        dc:identifier "{id}" ;
        rdfs:label "Facility number {id}"@en ;
        dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}> ;
        geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/{id}> .
    """


def gen_rdf_geometry(id, x, y):
    return f"""
    <http://id.cef-interstat.eu/sc/gf/geometry/{id}> a geo:Geometry ;
        rdfs:label "Geometry for facility {id}" ;
        geo:asWKT "POINT({x},{y})"^^geo:wktLiteral .
    """


def gen_rdf_quality(id, quality):
    return f"""
    <http://id.cef-interstat.eu/sc/gf/quality/{id}> a dqw:QualityAnnotation ;
        oa:hasBody <http://id.insee.fr/interstat/gf/QualityLevel/{quality}> ;
        oa:hasTarget <http://id.cef-interstat.eu/sc/gf/geometry/{id}> .
    """
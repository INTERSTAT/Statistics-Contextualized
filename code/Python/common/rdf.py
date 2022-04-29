"""
Helping functions for producing RDF triples
"""

# Lang tags
lang_en = "@en"
lang_fr = "@fr"
lang_it = "@it"

# Educational sector URI
sectors_uri = {
    "PU": "<http://id.insee.fr/interstat/gf/sector/public>",
    "PR": "<http://id.insee.fr/interstat/gf/sector/private>",
}

# Types of school characteristics
# See ontology here:https://github.com/INTERSTAT/Statistics-Contextualized/blob/main/pilots/gf/gf-ontology.ttl#L235
characteristic_types_uris = {
    "pge": "<http://id.insee.fr/interstat/gf/EducationCharacteristic/CL_PGE>",
    "pelem": "<http://id.insee.fr/interstat/gf/EducationCharacteristic/CL_PELEM>",
    "ep": "<http://id.insee.fr/interstat/gf/EducationCharacteristic/EP>",
}


def igf_characteristic(type, value):
    """
    For education facilities, this function helps to choose if a characteristic is present or not, or not applicable.
    """
    if str(value) == "nan" or str(value) == "X":
        return ""
    else:
        if value == "1":
            return f"igf:characteristic {characteristic_types_uris[type]}"
        else:
            return f"igf:absentCharacteristic {characteristic_types_uris[type]}"


def gen_rdf_facility(id, equipment_type, sector, lau, x, y, lang_tag=lang_en):
    # Handling facility subtype
    subtype = (
        "igf:EducationFacility"
        if equipment_type[0] == "C"
        else "igf:SportLeisureFacility"
    )
    # Producing sector prop
    sector_prop = f"igf:sector {sectors_uri[sector]} ;" if str(sector) != "nan" else ""
    lau_prop = f'igf:inLAU "{lau}"^^xsd:token ;' if str(lau) != "nan" else ""
    rdf_facility = f"""
    <http://id.cef-interstat.eu/sc/gf/facility/{id}> a igf:Facility ;
        a {subtype} ;
        rdfs:label "Facility code {id}"{lang_tag} ;    
        dc:identifier "{id}" ;
        {sector_prop}
        {lau_prop}
    """
    if str(x) == "nan" or str(y) == "nan":
        return "\n".join(
            [rdf_facility, f"""dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}> ."""])
    else:
        return "\n".join(
            [rdf_facility, f"""dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}> ;""",
             f"""geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/{id}> ."""])


def gen_rdf_french_facility(
        id, equipment_type, sector, lau, pge, pelem, ep, lang_tag=lang_en
):
    # Producing sector prop
    sector_prop = f"igf:sector {sectors_uri[sector]}" if str(sector) != "nan" else ""
    lau_prop = f'igf:inLAU "{lau}"^^xsd:token' if str(lau) != "nan" else ""

    pge_prop = igf_characteristic("pge", pge)
    pelem_prop = igf_characteristic("pelem", pelem)
    ep_prop = igf_characteristic("ep", ep)

    all_props_raw = [
        "a igf:Facility",
        "a igf:EducationFacility",
        f'rdfs:label "Facility code {id}"{lang_tag}',
        f'dc:identifier "{id}"',
        pge_prop,
        pelem_prop,
        ep_prop,
        sector_prop,
        lau_prop,
        f"dcterms:type <http://id.insee.fr/interstat/gf/FacilityType/{equipment_type}>",
        f"geo:hasGeometry <http://id.cef-interstat.eu/sc/gf/geometry/{id}>",
    ]

    # Filtering empty strings (they are related)
    all_props_filtered = [prop for prop in all_props_raw if prop != ""]
    all_props_str = " ;\n".join(all_props_filtered)
    rdf = f"<http://id.cef-interstat.eu/sc/gf/facility/{id}>\n{all_props_str} ."

    return rdf


def gen_rdf_geometry(id, x, y, lang_tag=lang_en):
    # Handling missing coordinates
    if str(x) == "nan" or str(y) == "nan":
        return ""
    return f"""
    <http://id.cef-interstat.eu/sc/gf/geometry/{id}> a geo:Geometry ;
        rdfs:label "Geometry for facility {id}"{lang_tag} ;
        geo:asWKT "POINT({x} {y})"^^geo:wktLiteral .
    """


def gen_rdf_quality(id, quality):
    if quality != "NOT_GEOLOCALIZED":
        return f"""
    <http://id.cef-interstat.eu/sc/gf/quality/{id}> a dqv:QualityAnnotation ;
        oa:hasBody <http://id.insee.fr/interstat/gf/QualityLevel/{quality}> ;
        oa:hasTarget <http://id.cef-interstat.eu/sc/gf/geometry/{id}> .
    """
    else:
        return ""

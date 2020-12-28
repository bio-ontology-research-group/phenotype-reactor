import logging
import json
from logging import log

import api.rdf.virtuoso as virt

logger = logging.getLogger(__name__)

class Associationsets:
    MIME_TYPE_JSON = "application/json"
    ASSOCIATIONSETS = {}

    def __init__(self) :
        associationset_filepath = "doc/associationsets.json"
        Associationsets.ASSOCIATIONSETS = json.load(open (associationset_filepath, "r"))
        logger.info("loaded association sets")

    def find_associationsets(self):
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                \nPREFIX pb: <http://phenomebrowser.net/> \
                \nPREFIX dcterms: <http://purl.org/dc/terms/> \
                \nPREFIX dc: <http://purl.org/dc/elements/1.1/> \
                \nSELECT ?associationset ?identifier ?label ?type ?description ?source ?download \
                \nFROM <http://phenomebrowser.net> \
                \nWHERE { \
                \n  ?associationset rdf:type pb:AssociationSet . \
                \n  ?associationset dc:identifier ?identifier . \
                \n  ?associationset rdfs:label ?label . \
                \n  ?associationset dc:description ?description . \
                \n  OPTIONAL { ?associationset dcterms:source ?source . }\
                \n  OPTIONAL { ?associationset pb:download ?download . } \
                \n  ?associationset pb:includeTypes ?type . \
                \n} ORDER BY asc(?label)'
        logger.debug("Executing find all associationset query")
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)

    def find_associationset_by_identifier(self, identifier):
        query = 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
                \nPREFIX pb: <http://phenomebrowser.net/> \
                \nPREFIX dcterms: <http://purl.org/dc/terms/> \
                \nPREFIX dc: <http://purl.org/dc/elements/1.1/> \
                \nSELECT ?associationset ?identifier ?label ?type ?description ?source ?download \
                \nFROM <http://phenomebrowser.net> \
                \nWHERE { \
                \n  ?associationset rdf:type pb:AssociationSet . \
                \n  ?associationset dc:identifier ?identifier . \
                \n  ?associationset rdfs:label ?label . \
                \n  ?associationset dc:description ?description . \
                \n  OPTIONAL { ?associationset dcterms:source ?source . }\
                \n  OPTIONAL { ?associationset pb:download ?download . } \
                \n  ?associationset pb:includeTypes ?type . \
                \n  FILTER (?identifier="' + identifier +'"^^xsd:string)\
                \n} ORDER BY asc(?label)'
        logger.debug("Executing find all associationset query")
        return (virt.execute_sparql(query, self.MIME_TYPE_JSON), query)

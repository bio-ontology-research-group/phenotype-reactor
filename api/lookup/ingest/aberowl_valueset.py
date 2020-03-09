import logging 

from api.lookup.ingest.source import Source

import api.lookup.ingest.aberowl_elasticsearch as aberowl_es
import api.lookup.lookup_elasticsearch as lookup_es  


logger = logging.getLogger(__name__)

class AberowlValueset(Source):

    def __init__(self, name, entity_type):
        super().__init__(name, entity_type)
        self.valueset = None
        self.entities = None
        self.ontolgy = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.ontology = aberowl_es.get_ontology(self.name)
        if len(self.ontology) > 0:
            self.ontology = self.ontology[0]
    
        self.data = aberowl_es.find_classes(self.name)
        logger.info("Finished fetching data: entities=%d", len(self.data))

    def map(self):
        self.valueset = {
                "valueset" : self.ontology['ontology'],
                "name" : self.ontology['name'],
                "description" : self.ontology['description']
            }
    
        self.entities = list(map(lambda entity:self.map_entity(entity), self.data))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        for entity in self.entities:
            lookup_es.index(lookup_es.ENTITY_INDEX_NAME, entity)
        
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, entity):
        obj = {}
        obj["entity"] =  entity['class']
        obj["valueset"] =  entity['ontology']
        obj["label"] =  entity['label'] if 'label' in entity else []
        obj["synonym"] =  entity['synonyms'] if 'synonyms' in entity  else []
        obj["definition"] =  entity['definition'] if 'definition' in entity  else []
        obj["identifier"] =  entity['identifier'] if 'identifier' in entity  else []
        obj["entity_type"] = self.entity_type
        return obj
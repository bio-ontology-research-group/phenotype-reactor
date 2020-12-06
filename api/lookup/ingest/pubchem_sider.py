import logging 

from api.ingest.source import Source
from api.rdf.namespace import PUBCHEM

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class PubchemValueset(Source):

    def __init__(self):
        super().__init__('PUBCHEM', 'Drug')
        self.valueset = None
        self.entities = None
        self.url = 'http://sideeffects.embl.de/media/download/drug_names.tsv'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', names=['id', 'name']) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : self.name,
            "entity_type" : self.entity_type
        }

        self.df['uri'] = self.df['id'].replace(regex=['CID'], value=PUBCHEM.uri)
        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        lookup_es.index_by_bulk(self.entities)
        # for entity in self.entities:
        #     lookup_es.index(lookup_es.ENTITY_INDEX_NAME, entity)
    
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, row):
        obj = {}
        obj["entity"] =  getattr(row, 'uri')
        obj["label"] =  [getattr(row, 'name')]
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        obj["identifier"] = getattr(row, 'id')
        return obj
import logging 

from api.lookup.ingest.source import Source
from api.rdf.namespace import DECIPHER

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class DecipherValueset(Source):

    def __init__(self):
        super().__init__('DECIPHER', 'Disease')
        self.valueset = None
        self.entities = None
        self.url = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t') 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : self.name
        }

        self.df =  self.df[self.df['#disease-db'] == self.name]
        self.df['disease-identifier'] = self.df['disease-identifier'].astype(str)
        self.df['disease_iri'] = self.df[['#disease-db', 'disease-identifier']].apply(lambda x: ':'.join(x), axis=1)
        self.df['disease_iri'] = self.df['disease_iri'].replace(regex=['DECIPHER:'], value=DECIPHER.uri)
        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        entity_set = set()
        for entity in self.entities:
            if entity["entity"] in entity_set:
                continue

            lookup_es.index(lookup_es.ENTITY_INDEX_NAME, entity)
            entity_set.add(entity["entity"])
    
        entity_set.clear()
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, row):
        obj = {}
        obj["entity"] =  getattr(row, 'disease_iri')
        obj["label"] =  [getattr(row, '_3')]
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        return obj
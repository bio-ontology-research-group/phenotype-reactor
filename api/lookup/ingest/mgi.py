import logging 
import datetime

from api.ingest.source import Source
from api.rdf.namespace import MGI

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class MGIValueset(Source):

    def __init__(self):
        super().__init__('MGI', 'Gene')
        self.valueset = None
        self.entities = None
        self.url = 'http://www.informatics.jax.org/downloads/reports/MRK_List2.rpt'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t') 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : "Mouse Genome Informatics",
            "entity_type" : self.entity_type,
            "created_on" : datetime.datetime.now()
        }

        self.df['mgi_uri'] = self.df['MGI Accession ID'].replace(regex=['MGI:'], value=MGI.uri + 'MGI:')
        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        lookup_es.index_by_bulk(self.entities)
    
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, row):
        obj = {}
        obj["entity"] =  getattr(row, 'mgi_uri')
        obj["label"] =  [getattr(row, '_7') , getattr(row, '_9')]
        obj["synonym"] =  [getattr(row, '_9')]
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        obj["identifier"] = getattr(row, '_1')
        return obj
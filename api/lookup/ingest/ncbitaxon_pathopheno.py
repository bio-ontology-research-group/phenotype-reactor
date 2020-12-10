import logging 

from api.ingest.source import Source
from api.rdf.namespace import PUBCHEM

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class NCBITaxonPathophenoValueset(Source):
    # Shrinked list of filtered ncbitaxon terms including only pathogens covered in pathopheno

    def __init__(self):
        super().__init__("NCBITaxon_Pathopheno", "Pathogen")
        self.valueset = None
        self.entities = None
        self.url = f'{self.sourcedir}/pathogens_phenotypes_shenay.txt'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_json(self.url) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : self.name,
            "entity_type" : self.entity_type,
            "custom": True
        }
        logger.info('head: %s', self.df.head())
        
        entity_iris = list(set(list(map(lambda row:getattr(row, 'TaxID'), self.df.itertuples()))))
        self.entities = list(filter(lambda entity: entity, map(lambda iri:self.map_entity(iri), entity_iris)))
        logger.info("Finished mapping data: entities=%d|%d", len(self.entities), len(entity_iris))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        lookup_es.index_by_bulk(self.entities)
    
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, iri):
        result = lookup_es.find_entity_by_iris([iri], 'NCBITAXON')
        if len(result) > 0:
            result[0]['valueset'] = self.valueset['valueset']
            return result[0]

        logger.info("not found: %s", iri)
import logging 

from django.conf import settings
from api.lookup.ingest.source import Source
from api.rdf.namespace import ENTREZ_GENE

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class NCBIGeneValueset(Source):

    informal_species = {
        'NCBITaxon:9913': 'cattle',
        'NCBITaxon:9031': 'chicken',
        'NCBITaxon:9823': 'pig',
        'NCBITaxon:9940': 'sheep',
        'NCBITaxon:9796': 'horse',
        'NCBITaxon:8022': 'rainbow_trout',
    }

    def __init__(self):
        super().__init__('NCBIGene', 'Gene')
        self.valueset = None
        self.entities = None
        self.url = 'http://ftp.ncbi.nih.gov/gene/DATA/gene_info.gz'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_csv(self.url, compression='gzip', sep='\t', error_bad_lines=False) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : "NCBI Gene"
        }

        self.df =  self.df[self.df['Symbol'] != 'NEWENTRY']
        self.df['GeneID'] = self.df['GeneID'].astype(str)
        self.df['GeneID'] = str(ENTREZ_GENE.uri) + self.df['GeneID']
        self.df['Synonyms'] = self.df['Synonyms'].astype(str)
        self.df['Other_designations'] = self.df['Other_designations'].astype(str)
        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        for entity in self.entities:
            lookup_es.index(lookup_es.ENTITY_INDEX_NAME, entity)
    
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, row):
        obj = {}
        obj["entity"] =  getattr(row, 'GeneID')
        obj["label"] =  getattr(row, 'Symbol')

        synonym = []
        synonym_col = getattr(row, 'Synonyms')
        if "-" != synonym_col:
            for syn in synonym_col.split('|'):
                syn = syn.strip()
                # unknown curies may occur here
                if syn[:12] == 'AnimalQTLdb:' and \
                        tax_curie in self.informal_species:
                    syn = self.informal_species[tax_curie] + 'QTL:' + syn[12:]
                    logger.info('AnimalQTLdb: CHANGED to: %s', syn)
                synonym.append(syn)

        other_designations = getattr(row, 'Other_designations')
        if other_designations != '-':
            synonym = synonym + other_designations.split('|')

        obj["synonym"] =  synonym
        obj["definition"] = [getattr(row, 'description')]
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        return obj
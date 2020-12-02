import logging 
import time

from django.conf import settings
from api.ingest.source import Source
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
        self.entities = []
        self.url_homosapiens = 'https://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz'
        self.url_musmusculus = 'https://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Mus_musculus.gene_info.gz'
        self.df = None
        self.columns = [
                'tax_id',
                'GeneID',
                'Symbol',
                'LocusTag',
                'Synonyms',
                'dbXrefs',
                'chromosome',
                'map_location',
                'description',
                'type_of_gene',
                'Symbol_from_nomenclature_authority',
                'Full_name_from_nomenclature_authority',
                'Nomenclature_status',
                'Other_designations',
                'Modification_date',
                'Feature_type',
            ]
        self.organism_type=['Homo sapiens', 'Mus musculus']

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df_homo = pd.read_csv(self.url_homosapiens, compression='gzip', sep='\t', error_bad_lines=False, names=self.columns) 
        self.df_mus = pd.read_csv(self.url_musmusculus, compression='gzip', sep='\t', error_bad_lines=False, names=self.columns) 
        logger.info("Finished fetching data homo sapien: entities=%d", self.df_homo.size)
        logger.info("Finished fetching data mus mus musculus: entities=%d", self.df_mus.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : "NCBI Gene"
        }
        self.map_gene(self.df_homo, self.organism_type[0])
        self.map_gene(self.df_mus, self.organism_type[1])

    def map_gene(self, df, organism_type):
        df =  df[df['Symbol'] != 'NEWENTRY']
        df['GeneID'] = df['GeneID'].astype(str)
        df['GeneUri'] = str(ENTREZ_GENE.uri) + df['GeneID']
        df['Synonyms'] = df['Synonyms'].astype(str)
        df['Other_designations'] = df['Other_designations'].astype(str)
        df['organism_type'] = organism_type
        logger.info('head: %s', df.head())
        self.entities = self.entities + list(map(lambda row:self.map_entity(row), df.itertuples()))
        logger.info("Finished mapping data: entities=%d|type=%s", len(self.entities), organism_type)

    def write(self):
        logger.info("Started indexing valueset %s", self.valueset)
        lookup_es.delete_valueset(self.valueset['valueset'])
        lookup_es.index(lookup_es.VALUESET_INDEX_NAME, self.valueset)
        data = []
        count = 0
        for entity in self.entities:
            data.append(entity)
            if len(data) % 100000 == 0 or count == len(self.entities) - 1:
                logger.info("indexing bulk of %d", len(data))
                lookup_es.index_by_bulk(data)
                data.clear()

            count += 1
    
        logger.info("Finished indexing valueset %s", self.valueset)

    def map_entity(self, row):
        obj = {}
        obj["entity"] =  getattr(row, 'GeneUri')
        obj["label"] =  [getattr(row, 'Symbol'), getattr(row, 'description') + ' ( ' + getattr(row, 'organism_type') + ' )'] #TODO : 'nan' symbol index error

        tax_num = getattr(row, 'tax_id')
        if isinstance(tax_num, int):
            tax_num = str(tax_num)

        tax_curie = ':'.join(('NCBITaxon', tax_num))
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
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        obj["identifier"] = getattr(row, 'GeneID')
        return obj
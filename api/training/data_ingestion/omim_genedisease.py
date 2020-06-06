import logging 
import csv
import pandas as pd

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import OMIM, OBO, ENTREZ_GENE

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path



logger = logging.getLogger(__name__)

TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class OMIMDiseaseGeneAssoc(Source):

    def __init__(self):
        super().__init__('OmimDiseaseGeneAssociations', '')
        self.entities = None
        self.url = 'https://omim.org/static/omim/data/mim2gene.txt'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data %s", self.name)
        #Headers MIM Number	MIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)	Entrez Gene ID (NCBI)	Approved Gene Symbol (HGNC)	Ensembl Gene ID (Ensembl)
        self.df = pd.read_csv(self.url, sep='\t', skiprows=5, skipfooter=13, names=["mim_number", "mim_entry_type", "entrez_gene_id", "gene_symbol", "ensembl_gene_id"]) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):

        self.df['mim_number'] = self.df['mim_number'].astype(str)
        self.df['mim_number'] = str(OMIM.uri) + self.df['mim_number']
        self.df['mim_entry_type'] = self.df['mim_entry_type'].astype(str)
        # self.df['entrez_gene_id'] = str(ENTREZ_GENE.uri) + self.df['entrez_gene_id']

        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started processing %s", self.name)
        outFile = join(TEST_SET_DIR, self.name + ".tsv")
        with open(outFile, 'w') as file:
            writer = csv.writer(file, delimiter='\t')

            for entity in self.entities:
                if not entity:
                    continue

                writer.writerow([entity['disease'], entity['relation'], entity['gene']])
    
        logger.info("Finished indexing valueset %s", self.name)

    def map_entity(self, row):
        if getattr(row, 'mim_entry_type') and getattr(row, 'mim_entry_type').strip() == 'gene' and 'nan' not in str(getattr(row, 'entrez_gene_id')):
            obj = {}
            obj["disease"] =  "<" + getattr(row, 'mim_number') + ">"
            obj["gene"] = "<" + str(ENTREZ_GENE.uri) + str(int(getattr(row, 'entrez_gene_id'))) + ">"
            obj["relation"] =  "<" + str(OBO.PATO_0001668) + ">"
            return obj
        else:
            return None
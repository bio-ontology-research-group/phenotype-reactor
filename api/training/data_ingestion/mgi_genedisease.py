import logging 
import json
import csv
import pandas as pd

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import ENTREZ_GENE, OMIM, MGI, OBO

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path


logger = logging.getLogger(__name__)

TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class MGIHumanMouseGeneDiseaseAssoc(Source):

    def __init__(self):
        super().__init__('MGIHumanMouseGeneDiseaseAssociations', '')
        self.entities = None
        self.url = "http://www.informatics.jax.org/downloads/reports/MGI_DO.rpt"
        self.df = None

    def fetch(self):
        logger.info("Started fetching data %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t') 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.df['DO Disease ID'] = self.df['DO Disease ID'].replace(regex=[':'], value='_')

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
        if str(getattr(row, '_7')) == 'nan':
            return None
            
        obj = {}
        obj["disease"] =  str(OBO.uri) +  getattr(row, '_1')
        obj["gene"] = str(ENTREZ_GENE.uri) + str(int(getattr(row, '_7')))
        obj["relation"] =  str(OBO.PATO_0001668)
        return obj
import logging 
import csv
import pandas as pd
import json

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import OBO, ENTREZ_GENE

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path

logger = logging.getLogger(__name__)

TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class CuratedDisgenetAssoc(Source):

    def __init__(self):
        super().__init__('CuratedDisgenetAssociation', '')
        self.entities = None
        self.url = join(self.sourcedir, 'curated_disgenet.dict')
        self.dict = None

    def fetch(self):
        logger.info("Started fetching data %s", self.name)
        source_file = open(self.url, "r")
        self.dict = json.load(source_file) 
        logger.info("Finished fetching data: entities=%d", len(self.dict))

    def map(self):
        self.entities = list(map(lambda key:self.map_entity(key), self.dict))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started processing %s", self.name)
        outFile = join(TEST_SET_DIR, self.name + ".tsv")
        with open(outFile, 'w') as file:
            writer = csv.writer(file, delimiter='\t')

            for entity in self.entities:
                for gene in entity['gene']:
                    writer.writerow([entity['disease'], entity['relation'], gene])
    
        logger.info("Finished processing %s", self.name)

    def map_entity(self, key):
        obj = {}
        obj["disease"] = str(OBO.uri) + key.replace(':', '_')
        
        gene_list = []
        for gene in  set(self.dict[key]):
            gene_list.append((str(ENTREZ_GENE.uri) + gene))

        obj["gene"] =  gene_list
        obj["relation"] =  str(OBO.PATO_0001668)
        return obj
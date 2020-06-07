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

class PathoPathogenDiseaseAssoc(Source):

    def __init__(self):
        super().__init__('PathoPathogenDiseaseAssociations', '')
        self.entities = None
        self.url = join(self.sourcedir, 'pathogens_phenotypes_shenay.txt')
        self.df = None

    def fetch(self):
        logger.info("Started fetching data %s", self.name)
        #Headers MIM Number	MIM Entry Type (see FAQ 1.3 at https://omim.org/help/faq)	Entrez Gene ID (NCBI)	Approved Gene Symbol (HGNC)	Ensembl Gene ID (Ensembl)
        self.df = pd.read_json(self.url) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        logger.info('head: %s', self.df.head())
        self.entities = list(map(lambda row:self.map_entity(row), self.df.itertuples()))
        logger.info("Finished mapping data: entities=%d", len(self.entities))

    def write(self):
        logger.info("Started processing %s", self.name)
        outFile = join(TEST_SET_DIR, self.name + ".tsv")
        with open(outFile, 'w') as file:
            writer = csv.writer(file, delimiter='\t')

            for entity in self.entities:
                for disease in entity['disease']:
                    writer.writerow([entity['pathogen'], entity['relation'], disease])
    
        logger.info("Finished processing %s", self.name)

    def map_entity(self, row):
        obj = {}
        obj["pathogen"] = row.TaxID
        diseases = []
        for disease in row.Diseases:
            diseases.append(disease['id'])

        obj["disease"] =  diseases
        obj["relation"] =  str(OBO.PATO_0001668)
        return obj
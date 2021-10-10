import logging 
import datetime
import xmltodict
import urllib

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import UNIPROT
from gzip import GzipFile

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class UniProtValueset(Source):


    def __init__(self):
        super().__init__('UniProt', 'Protein')
        self.valueset = None
        self.entities = []
        self.url = 'https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.xml.gz'

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        with urllib.request.urlopen(self.url) as response:
            data = xmltodict.parse(GzipFile(fileobj=response))
            self.entities = data['uniprot']["entry"]
            logger.info("Finished fetching data human: entities=%d", len(self.entities))

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : "UNIPROT SWISS Human",
            "entity_type" : self.entity_type,
            "custom": True,
            "created_on" : datetime.datetime.now()
        }
        
        logger.info('head: %s', str(self.entities[0]))
        self.entities = list(map(lambda row:self.map_entity(row), self.entities))
        self.entities  = [item for sublist in self.entities for item in sublist]
        logger.info("Finished mapping data: entities=%d", len(self.entities))

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
        logger.info("Processing protein: %s", str(row['accession']))
        if isinstance(row['accession'], list):
            obj_list= []
            for accession in row['accession']:
                obj_list.append(self.map_instance(accession, row))
            return obj_list
        else:
            return [self.map_instance(row['accession'], row)]

    def map_instance(self, accession, row):
        obj = {}
        obj["entity"] =  str(UNIPROT.uri) + accession
        if '#text' in row['protein']['recommendedName']['fullName']:
            obj["label"] =  [row['protein']['recommendedName']['fullName']['#text']]
        else:
            obj["label"] =  [row['protein']['recommendedName']['fullName']]

        obj["synonym"] =  [row['name']]
        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        obj["identifier"] = accession
        return obj

import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import OMIM

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class OMIMValueset(Source):

    def __init__(self):
        super().__init__('OMIM', 'Disease')
        self.valueset = None
        self.entities = None
        self.url = 'https://data.omim.org/downloads/' + settings.OMIM_KEY + '/mimTitles.txt'
        self.df = None

    def fetch(self):
        logger.info("Started fetching data for valueset %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', skiprows=3, skipfooter=13, names=["prefix",	"mim_number", "preferred_title", "alternative_titles", "included_titles"]) 
        logger.info("Finished fetching data: entities=%d", self.df.size)

    def map(self):
        self.valueset = {
            "valueset" : self.name,
            "name" : "Online Mendelian Inheritance in Man"
        }

        self.df =  self.df[self.df['prefix'] != "Caret"]
        self.df['mim_number'] = self.df['mim_number'].astype(str)
        self.df['mim_number'] = str(OMIM.uri) + self.df['mim_number']
        self.df['preferred_title'] = self.df['preferred_title'].astype(str)
        self.df['alternative_titles'] = self.df['alternative_titles'].astype(str)
        self.df['included_titles'] = self.df['included_titles'].astype(str)

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
        obj["entity"] =  getattr(row, 'mim_number')
        obj["label"] =  [getattr(row, 'preferred_title')]
        obj["synonym"] = [] 
        pref_titles = getattr(row, 'preferred_title')
        if pref_titles and 'NaN' not in pref_titles and 'nan' not in pref_titles:
            obj["synonym"] = [ item.strip() for item in pref_titles.split(';') if item]

        alternative_titles = getattr(row, 'alternative_titles')
        if alternative_titles and 'NaN' not in alternative_titles and 'nan' not in alternative_titles:
            obj["synonym"] = obj["synonym"]  + [ item.strip() for item in alternative_titles.split(';') if item]

        included_titles = getattr(row, 'included_titles')
        if included_titles and 'NaN' not in included_titles and 'nan' not in included_titles:
            obj["synonym"] = obj["synonym"]  + [ item.strip() for item in included_titles.split(';') if item]

        obj["valueset"] =  self.name
        obj["entity_type"] = self.entity_type
        return obj
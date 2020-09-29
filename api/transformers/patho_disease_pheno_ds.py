import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class PathoDiseasePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('PathoDiseasePhenoDS', target_dir)
        self.url = f'{self.sourcedir}/patho_diseases_phenotypes.json'
        self.df = None
        self.rdf_filename = "patho_diseasephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_json(self.url) 
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        logger.info('head: %s', self.df.head())
        for index, row in self.df.iterrows():
            self.map_association(row)
        self.resolve_display()
        logger.info("Finished mapping data: assoications=%d", self.df.size)

    def write(self):
        logger.info("Writing rdf fo dataset%s", self.name)
        self.store.serialize(f'{self.target_dir}/{self.rdf_filename}.{self.rdf_ext}', format=settings.EXPORT_FORMAT, max_depth=3)
        self.store.remove((None, None, None))
        del self.df
        logger.info("Finished rdf writting for %s with size:%d", self.name, len(self.store))

    def map_association(self, row):
        disease = self.store.resource(row.DOID)
        disease.add(RDF.type, PHENO.Disease)

        for phenotype in row.Phenotypes:
            phenotypeRes = self.store.resource(phenotype['id'])
            phenotypeRes.add(RDF.type, PHENO.Phenotype)
            association = create_phenotypic_association(self.store, disease, phenotypeRes)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)

            add_association_provenance(self.store, association, creator='Senay Kafkas', 
                created_on='2019-06-03', source='https://www.nature.com/articles/s41597-019-0090-x')

    def resolve_display(self):
        diseases  = list(set(self.store.subjects(RDF.type, PHENO.Disease)))
        diseases_iris = list(map(lambda i:str(i), diseases))
        logger.info("Resolving iris; total:%d", len(diseases_iris))
        diseases_indices = lookup_es.find_entity_by_iris(diseases_iris, 'DOID')
        self.add_label(diseases_iris, diseases_indices)
        
        self.add_phenotype_label()
        self.add_evidence_label()
        
        

    
import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class MondoDiseasePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('textmined_mondo_disease_phenotypes', target_dir)
        self.url = f'{self.sourcedir}/mondo-pheno_shenay.txt'
        self.df = None
        self.rdf_filename = "mondo_diseasephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t') 
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.Phenotype_ID = self.df.Phenotype_ID.replace(regex=[':'], value='_')
        self.df.Mondo_ID = self.df.Mondo_ID.replace(regex=[':'], value='_')
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
        disease = self.store.resource(str(OBO.uri) + row.Mondo_ID)
        disease.add(RDF.type, PHENO.Disease)
        phenotype = self.store.resource(str(OBO.uri) + row.Phenotype_ID)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(self.store, disease, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(self.store, association, creator='Senay Kafkas',
         source='https://www.ncbi.nlm.nih.gov/pubmed/30809638')
        self.add_association(association)
        

    def resolve_display(self):
        diseases  = list(set(self.store.subjects(RDF.type, PHENO.Disease)))
        diseases_iris = list(map(lambda i:str(i), diseases))
        diseases_indices = lookup_es.find_entity_by_iris(diseases_iris, 'MONDO')
        logger.info("Resolving iris; total:%d|found:%d", len(diseases_iris), len(diseases_indices))
        self.add_label(diseases_iris, diseases_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
        
        
    


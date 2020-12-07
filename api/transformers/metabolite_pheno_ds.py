import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class MetabolitePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('textmined_metabolite_phenotypes', target_dir)
        self.url = f'{self.sourcedir}/metabolite_pheno_shenay.txt'
        self.df = None
        self.rdf_filename = "metabolitephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t') 
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.CHEBI_ID = self.df.CHEBI_ID.replace(regex=[':'], value='_')
        self.df.Phenotype_ID = self.df.Phenotype_ID.replace(regex=[':'], value='_')
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
        metabolite = self.store.resource(str(OBO.uri) + row.CHEBI_ID)
        metabolite.add(RDF.type, PHENO.Metabolite)
        phenotype = self.store.resource(str(OBO.uri) + row.Phenotype_ID)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(self.store, metabolite, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(self.store, association, creator='Senay Kafkas',
         source='https://www.ncbi.nlm.nih.gov/pubmed/30809638')
        self.add_association(association)

    def resolve_display(self):
        metabolites = list(set(self.store.subjects(RDF.type, PHENO.Metabolite)))
        metabolites_iris = list(map(lambda i:str(i), metabolites))
        logger.info("Resolving iris; total:%d", len(metabolites_iris))
        metabolites_indices = lookup_es.find_entity_by_iris(metabolites_iris, 'CHEBI')
        self.add_label(metabolites_iris, metabolites_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
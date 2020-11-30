import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class DrugPhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('DrugPhenoDS', target_dir)
        self.url = f'{self.sourcedir}/drug_phenotypes_sara.txt'
        self.df = None
        self.rdf_filename = "drugphenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep=' ', names=['drug', 'phenotype']) 
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.phenotype = self.df.phenotype.replace(regex=['<'], value='').replace(regex=['>'], value='')
        self.df.drug = self.df.drug.replace(regex=['CID'], value='')
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
        drug = self.store.resource(str(PUBCHEM.uri) + row.drug)
        drug.add(RDF.type, PHENO.Drug)
        phenotype = self.store.resource(row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(self.store, drug, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(self.store, association, creator='Sara Althubaiti', created_on='2019-03-12',
         source="http://phenomebrowser.net/downloads#sider")

    def resolve_display(self):
        drug  = list(set(self.store.subjects(RDF.type, PHENO.Drug)))
        drug_iris = list(map(lambda i:str(i), drug))
        logger.info("Resolving iris; total:%d", len(drug_iris))
        drug_indices = lookup_es.find_entity_by_iris(drug_iris, 'PUBCHEM')
        self.add_label(drug_iris, drug_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
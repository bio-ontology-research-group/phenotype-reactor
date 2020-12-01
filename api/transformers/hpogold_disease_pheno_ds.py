import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class HpoGoldDiseasePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('HpoGoldDiseasePhenoDS', [PHENO.Disease], target_dir)
        self.url = f'{self.sourcedir}/HPO.disease.phenotypes.4sim.txt'
        self.rows = []
        self.rdf_filename = "hpogold_diseasephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        with open(self.url, 'r') as temp_f:
            lines = temp_f.readlines()
            for l in lines:
                self.rows.append(l.strip().split('\t'))

        logger.info("Finished reading dataset: assoications=%d", len(self.rows))

    def map(self):
        for row in self.rows:
            self.map_association(row)
        self.resolve_display()
        logger.info("Finished mapping data: assoications=%d", len(self.rows))

    def write(self):
        logger.info("Writing rdf fo dataset%s", self.name)
        self.store.serialize(f'{self.target_dir}/{self.rdf_filename}.{self.rdf_ext}', format=settings.EXPORT_FORMAT, max_depth=3)
        self.store.remove((None, None, None))
        logger.info("Finished rdf writting for %s with size:%d", self.name, len(self.store))

    def map_association(self, row):
        disease_uri = row[0].strip().replace('OMIM:', str(OMIM.uri))
        disease = self.store.resource(disease_uri)
        disease.add(RDF.type, PHENO.Disease)
        
        for pheno in row[1:]:
            pheno_uri = str(OBO.uri) + pheno.strip().replace(':','_')
            phenotype = self.store.resource(pheno_uri)
            phenotype.add(RDF.type, PHENO.Phenotype)
            association = create_phenotypic_association(self.store, disease, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(self.store, association, creator='HPO_GOLD', created_on='2019-03-12',
            source="https://www.ncbi.nlm.nih.gov/pubmed/20087340")
            self.add_association(association)

    def resolve_display(self):
        disease  = list(set(self.store.subjects(RDF.type, PHENO.Disease)))
        disease_iris = list(map(lambda i:str(i), disease))
        disease_indices = lookup_es.find_entity_by_iris(disease_iris, 'OMIM')
        logger.info("Resolving iris; total:%d|found:%d",  len(disease_iris), len(disease_indices))
        self.add_label(disease_iris, disease_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
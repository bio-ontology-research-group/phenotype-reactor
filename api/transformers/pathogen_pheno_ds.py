import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class PathogenPhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('pathopheno_pathogen_phenotypes', target_dir)
        self.url = f'{self.sourcedir}/pathogens_phenotypes_shenay.txt'
        self.df = None
        self.rdf_filename = "pathogenphenotype"

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
        pathogen = self.store.resource(row.TaxID)
        pathogen.add(RDF.type, PHENO.Pathogen)
        evidences = []
        for method in row.Diseases[0]['method'].split(","):
            if not method.strip():
                continue
            
            if "text mining" in method:
                evidences.append(OBO.ECO_0007669)
            elif "manual curation" in method:
                evidences.append(OBO.ECO_0000305)

        for phenotype in row.Phenotypes:
            phenotypeRes = self.store.resource(phenotype['id'])
            phenotypeRes.add(RDF.type, PHENO.Phenotype)
            association = create_phenotypic_association(self.store, pathogen, phenotypeRes)
            for evidence in evidences:
                association.add(OBO.RO_0002558, evidence)

            add_association_provenance(self.store, association, creator='Senay Kafkas', 
                created_on='2019-06-03', source='https://pubmed.ncbi.nlm.nih.gov/31160594')
            self.add_association(association)


    def resolve_display(self):
        pathogens  = list(set(self.store.subjects(RDF.type, PHENO.Pathogen)))
        pathogen_iris = list(map(lambda i:str(i), pathogens))
        logger.info("Resolving iris; total:%d", len(pathogen_iris))
        pathogen_indices = lookup_es.find_entity_by_iris(pathogen_iris, 'NCBITAXON')
        self.add_label(pathogen_iris, pathogen_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
        
        

    
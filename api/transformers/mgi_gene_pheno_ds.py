import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class MGIGenePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('MGIGenePhenoDS', target_dir)
        self.url = f'http://www.informatics.jax.org/downloads/reports/MGI_PhenoGenoMP.rpt'
        self.df = None
        self.rdf_filename = "mgi_genephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', names=['allelic_composition',	'allele_symbol', 
        'genetic_background', 'mammalian_phenotype_id', 'pubmed_id', 'mgi_id'])
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.mammalian_phenotype_id = self.df.mammalian_phenotype_id.replace(regex=[':'], value='_')
        self.df.pubmed_id = self.df.pubmed_id.astype(str)
        logger.info('head: %s', self.df.head())

        for index, row in self.df.iterrows():
            self.map_association(row)
        self.resolve_display()
        logger.info("Finished mapping data: assoications=%d", self.df.size)

    def write(self):
        logger.info("Writing rdf fo dataset: %s", self.name)
        self.store.serialize(f'{self.target_dir}/{self.rdf_filename}.{self.rdf_ext}', format=settings.EXPORT_FORMAT, max_depth=3)
        self.store.remove((None, None, None))
        del self.df
        logger.info("Finished rdf writting for %s with size:%d", self.name, len(self.store))

    def map_association(self, row):
        for gene_part in row.mgi_id.strip().split('|'):
            gene = self.store.resource(str(MGI.uri) + gene_part)
            gene.add(RDF.type, PHENO.Gene)

            phenotype = self.store.resource(str(OBO.uri) + row.mammalian_phenotype_id)
            phenotype.add(RDF.type, PHENO.Phenotype)
        
            association = create_phenotypic_association(self.store, gene, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0000501)
        
            created_on = ''
            sources = 'http://www.informatics.jax.org/downloads/reports/index.html#pheno'
            creator = 'MGI'
            add_association_provenance(self.store, association, creator=creator, created_on=created_on, source=sources)
        

    def resolve_display(self):
        gene  = list(set(self.store.subjects(RDF.type, PHENO.Gene)))
        gene_iris = list(map(lambda i:str(i), gene))
        gene_indices = lookup_es.find_entity_by_iris(gene_iris, 'MGI')
        logger.info("Resolving iris; total:%d|found:%d",  len(gene_iris), len(gene_indices))
        self.add_label(gene_iris, gene_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
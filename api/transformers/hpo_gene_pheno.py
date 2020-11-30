import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)
HPO_PIPELINE_BASE_URL = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/util/annotation/'

class HPOGenePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('HPOGenePhenoDS', target_dir)
        self.url = f'{HPO_PIPELINE_BASE_URL}/genes_to_phenotype.txt'
        self.df = None
        self.rdf_filename = "hpo_genephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', skiprows=1, names=['entrez_gene_id', 'entrez-gene-symbol', 'hpo_term_id', 'hpo_term_id', 
        'frequency_raw', 'frequency_hpo', 'additional_info_from_gd_source', 'gd_source', 'disease_id'])
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.hpo_term_id = self.df.hpo_term_id.replace(regex=[':'], value='_')
        self.df.entrez_gene_id = self.df.entrez_gene_id.astype(str)
        self.df.gd_source = self.df.gd_source.astype(str)
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
        phenotype = self.store.resource(str(OBO.uri) + row.hpo_term_id)
        phenotype.add(RDF.type, PHENO.Phenotype)

        geneRes = self.store.resource(str(ENTREZ_GENE.uri) + row.entrez_gene_id)
        geneRes.add(RDF.type, PHENO.Gene)
        
        association = create_phenotypic_association(self.store, geneRes, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0000501)
        
        created_on = '2020-10-12'
        sources = 'https://hpo.jax.org/app/download/annotation'
        creator = 'HPO'
        add_association_provenance(self.store, association, creator=creator, created_on=created_on, source=sources)
        

    def resolve_display(self):
        genes  = list(set(self.store.subjects(RDF.type, PHENO.Gene)))
        genes_iris = list(map(lambda i:str(i), genes))
        logger.info("Resolving iris; total:%d", len(genes_iris))
        gene_indices = lookup_es.find_entity_by_iris(genes_iris, 'NCBIGene')
        self.add_label(genes_iris, gene_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
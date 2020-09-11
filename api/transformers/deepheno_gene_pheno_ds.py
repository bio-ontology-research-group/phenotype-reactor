import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class DeepphenoGenePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('DeepphenoGenePhenoDS', target_dir)
        self.url = f'{self.sourcedir}/deeppheno_maxat.txt'
        self.df = None
        self.rdf_filename = "deep_genephenotype"

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', names=['gene', 'phenotype', 'score'])
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.phenotype = self.df.phenotype.replace(regex=[':'], value='_')
        self.df.gene = self.df.gene.astype(str)
        logger.info('head: %s', self.df.head())
        self.resolve_display()
        logger.info("Finished mapping data: assoications=%d", self.df.size)

    def write(self):
        logger.info("Writing rdf fo dataset%s", self.name)

        split_count = 1
        for index, row in self.df.iterrows():
            self.map_association(row)
            if index > 0 and index % 500000 == 0:
                self.resolve_display()
                self.store.serialize(f'{self.target_dir}/{self.rdf_filename}-{split_count}.{self.rdf_ext}', format=settings.EXPORT_FORMAT, max_depth=3)
                logger.info("rdf writting for %s with size:%d", self.name, len(self.store))
                self.store.remove((None, None, None))
                split_count += 1
        

        self.resolve_display()
        self.store.serialize(f'{self.target_dir}/{self.rdf_filename}-{split_count}.{self.rdf_ext}', format=settings.EXPORT_FORMAT, max_depth=3)       
        self.store.remove((None, None, None))
        del self.df
        logger.info("Finished rdf writting for %s with size:%d", self.name, len(self.store))

    def map_association(self, row):
        gene = self.store.resource(str(ENTREZ_GENE.uri) + row.gene)
        gene.add(RDF.type, PHENO.Gene)
        phenotype = self.store.resource(str(OBO.uri) + row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(self.store, gene, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(self.store, association, creator='Maxat Kulmanov', 
            created_on='2020-03-25', source='https://www.biorxiv.org/content/10.1101/839332v2')

    def resolve_display(self):
        genes  = list(set(self.store.subjects(RDF.type, PHENO.Gene)))
        genes_iris = list(map(lambda i:str(i), genes))
        logger.info("Resolving iris; total:%d", len(genes_iris))
        gene_indices = lookup_es.find_entity_by_iris(genes_iris, 'NCBIGene')
        self.add_label(genes_iris, gene_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
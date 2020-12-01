import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)

class TextminedhenoGenePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('textmined gene-phenotypes', [PHENO.Gene], target_dir)
        self.url = f'{self.sourcedir}/genephenotypes_textmined_senay.txt'
        self.df = None
        self.rdf_filename = "textmined_genephenotype"
        self.study_source = 'https://www.ncbi.nlm.nih.gov/pubmed/30809638'

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', names=['mgi', 'entrez_gene',  'phenotype', 'score']) 
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df.mgi = self.df.mgi.astype(str).replace(regex=['nan'], value='')
        self.df[['gene1', 'gene2']] = self.df.entrez_gene.str.split("_#_", expand = True)
        logger.info('head: %s', self.df.head())
        self.resolve_display()
        logger.info("Finished mapping data: assoications=%d", self.df.size)

    def write(self):
        logger.info("Writing rdf fo dataset%s", self.name)

        split_count = 1
        for index, row in self.df.iterrows():
            self.map_association(row)
            if index > 0 and index % 150000 == 0:
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
        phenotype = self.store.resource(str(OBO.uri) + row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        
        if row.mgi.strip():
            mgi = self.store.resource(str(MGI.uri) + row.mgi.strip())
            mgi.add(RDF.type, PHENO.Gene)
            association = create_phenotypic_association(self.store, mgi, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(self.store, association, creator='Senay Kafkas', 
                created_on='2019-01-06', source=self.study_source)
            self.add_association(association)

        if row.gene1:
            gene = self.store.resource(str(ENTREZ_GENE.uri) + row.gene1.strip())
            gene.add(RDF.type, PHENO.Gene)
            association = create_phenotypic_association(self.store, gene, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(self.store, association, creator='Senay Kafkas', 
                created_on='2019-01-06', source=self.study_source)
            self.add_association(association)

        if row.gene2:
            for geneitem in row.gene2.split('##'):
                gene = self.store.resource(str(ENTREZ_GENE.uri) + geneitem.strip())
                gene.add(RDF.type, PHENO.Gene)
                association = create_phenotypic_association(self.store, gene, phenotype)
                association.add(OBO.RO_0002558, OBO.ECO_0007669)
                add_association_provenance(self.store, association, creator='Senay Kafkas', 
                    created_on='2019-01-06', source=self.study_source)
                self.add_association(association)


    def resolve_display(self):
        genes  = list(set(self.store.subjects(RDF.type, PHENO.Gene)))
        genes_iris = list(map(lambda i:str(i), genes))

        mgi_gene=list(set(filter(lambda x: find_valueset(x) == 'MGI', genes_iris)))
        mgi_indices = lookup_es.find_entity_by_iris(mgi_gene, 'MGI')
        logger.info("Resolving iris; total:%d|found:%d", len(mgi_gene), len(mgi_indices))
        self.add_label(mgi_gene, mgi_indices)

        ncbi_gene=list(set(filter(lambda x: find_valueset(x) == 'NCBIGene', genes_iris)))
        ncbi_indices = lookup_es.find_entity_by_iris(ncbi_gene, 'NCBIGene')
        logger.info("Resolving iris; total:%d|found:%d", len(ncbi_gene), len(ncbi_indices))
        self.add_label(ncbi_gene, ncbi_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
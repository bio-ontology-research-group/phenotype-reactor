import logging 

from django.conf import settings
from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, find_valueset
from api.rdf.association_model import *
from api.rdf.rdf_source import RDFSource

import api.lookup.lookup_elasticsearch as lookup_es  
import pandas as pd


logger = logging.getLogger(__name__)
HPO_PIPELINE_BASE_URL = 'http://purl.obolibrary.org/obo/hp/hpoa/'

class HPODiseasePhenoDS(RDFSource):

    def __init__(self, target_dir):
        super().__init__('hpo_disease_phenotypes', target_dir)
        self.url = f'{HPO_PIPELINE_BASE_URL}phenotype.hpoa'
        self.df = None
        self.rdf_filename = "hpo_diseasephenotype"
        self.pheno_disease_dict = {}

    def fetch(self):
        logger.info("Started reading dataset: %s", self.name)
        self.df = pd.read_csv(self.url, sep='\t', skiprows=4)
        logger.info("Finished reading dataset: assoications=%d", self.df.size)

    def map(self):
        self.df['HPO_ID'] = self.df['HPO_ID'].replace(regex=[':'], value='_')
        self.df['#DatabaseID'] = self.df['#DatabaseID'].replace(regex=['DECIPHER:'], value=DECIPHER.uri)
        self.df['#DatabaseID'] = self.df['#DatabaseID'].replace(regex=['OMIM:'], value=OMIM.uri)
        self.df['#DatabaseID'] = self.df['#DatabaseID'].replace(regex=['ORPHA:'], value=ORPHA.uri)

        self.df.Reference = self.df.Reference.replace(regex=['DECIPHER:'], value=DECIPHER.uri)
        self.df.Reference = self.df.Reference.replace(regex=['OMIM:'], value=OMIM.uri)
        self.df.Reference = self.df.Reference.replace(regex=['ORPHA:'], value=ORPHA.uri)
        self.df.Reference = self.df.Reference.replace(regex=['PMID:'], value=PMID.uri)
        self.df.Reference = self.df.Reference.replace(regex=['ISBN-13:'], value=ISBN.uri)
        self.df.Reference = self.df.Reference.replace(regex=['ISBN-10:'], value=ISBN.uri)
        self.df.Reference = self.df.Reference.astype(str).replace(regex=['nan'], value='')
        self.df.Biocuration = self.df.Biocuration.astype(str)
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
        phenotype = self.store.resource(str(OBO.uri) + row['HPO_ID'].strip())
        phenotype.add(RDF.type, PHENO.Phenotype)

        diseaseRes = self.store.resource(row['#DatabaseID'].strip())
        diseaseRes.add(RDF.type, PHENO.Disease)
        
        dict_key = row['HPO_ID'] + ":" + row['#DatabaseID']
        association = None
        if dict_key not in self.pheno_disease_dict:
            association = create_phenotypic_association(self.store, diseaseRes, phenotype)

            evidence = None
            if 'IEA' in row['Evidence']:
                evidence = OBO.ECO_0000501
            elif 'PCS' in row['Evidence']:
                evidence = OBO.ECO_0006016
            elif 'ICS' in row['Evidence']:
                evidence = OBO.ECO_0006018
            elif 'TAS' in row['Evidence']:
                evidence = OBO.ECO_0000033

            association.add(OBO.RO_0002558, evidence)
            self.pheno_disease_dict[dict_key] = association
        else:
            association = self.pheno_disease_dict[dict_key]

        row.Biocuration = row.Biocuration.split(';')
        creator = []
        created_on = None

        for creator_field in row.Biocuration:
            creator = (creator_field if creator_field.find('[') == -1 else creator_field[:creator_field.find('[')])
            created_on = (creator_field[creator_field.find('[') + 1: len(creator_field) - 1] if creator_field.find('[') > -1 else None)

        sources = ['https://pubmed.ncbi.nlm.nih.gov/30476213'] 
        for ref in row.Reference.split(";"):
            if OMIM.uri in ref or DECIPHER.uri in ref or ORPHA.uri in ref:
                continue
            sources.append(ref)

        add_association_provenance(self.store, association, creator=creator, created_on=created_on, source=sources)
        self.add_association(association)
        

    def resolve_display(self):
        diseases  = list(set(self.store.subjects(RDF.type, PHENO.Disease)))
        diseases_iris = list(map(lambda i:str(i), diseases))

        mim_disease=list(set(filter(lambda x: find_valueset(x) == 'OMIM', diseases_iris)))
        mim_indices = lookup_es.find_entity_by_iris(mim_disease, 'OMIM')
        logger.info("Resolving iris; total:%d|found:%d", len(mim_disease), len(mim_indices))
        self.add_label(mim_disease, mim_indices)

        decipher_disease=list(set(filter(lambda x: find_valueset(x) == 'DECIPHER', diseases_iris)))
        decipher_indices = lookup_es.find_entity_by_iris(decipher_disease, 'DECIPHER')
        logger.info("Resolving iris; total:%d|found:%d", len(decipher_disease), len(decipher_indices))
        self.add_label(decipher_disease, decipher_indices)

        ordo_disease=list(set(filter(lambda x: find_valueset(x) == 'ordo', diseases_iris)))
        ordo_indices = lookup_es.find_entity_by_iris(ordo_disease, 'ordo')
        logger.info("Resolving iris; total:%d|found:%d", len(ordo_disease), len(ordo_indices))
        self.add_label(ordo_disease, ordo_indices)

        self.add_phenotype_label()
        self.add_evidence_label()
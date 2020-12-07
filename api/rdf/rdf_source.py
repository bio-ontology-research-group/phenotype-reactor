import logging

import api.lookup.lookup_elasticsearch as lookup_es  

from django.conf import settings

from api.ingest.source import Source
from api.rdf.namespace import RDFLIB_FORMAT_DIC, PHENO, OBO, find_valueset
from api.rdf.association_model import create_graph, create_associationset

from rdflib.namespace import RDFS
from rdflib.term import URIRef
from rdflib import RDF, XSD, Literal
from api.associationsets import Associationsets


logger = logging.getLogger(__name__)

class RDFSource(Source):

    def __init__(self, name, target_dir) :
        super().__init__(name, '')
        self.target_dir = target_dir
        self.rdf_ext = RDFLIB_FORMAT_DIC[settings.EXPORT_FORMAT]
        self.store = create_graph()
        if name in Associationsets.ASSOCIATIONSETS:
            self.associationset = create_associationset(self.store, Associationsets.ASSOCIATIONSETS[name])

    def add_phenotype_label(self):
        phenotypes  = list(set(self.store.subjects(RDF.type, PHENO.Phenotype)))
        phenotypes_iris = list(map(lambda i:str(i), phenotypes))
        
        hp_phenotypes=list(set(filter(lambda x: find_valueset(x) == 'HP', phenotypes_iris)))
        hp_indices = lookup_es.find_entity_by_iris(hp_phenotypes, 'HP')
        logger.info("Resolving iris; total:%d|found:%d", len(hp_phenotypes), len(hp_indices))
        self.add_label(hp_phenotypes, hp_indices)
        
        mp_phenotypes=list(set(filter(lambda x: find_valueset(x) == 'MP', phenotypes_iris)))
        mp_indices = lookup_es.find_entity_by_iris(mp_phenotypes, 'MP')
        logger.info("Resolving iris; total:%d|found:%d", len(mp_phenotypes), len(mp_indices))
        self.add_label(mp_phenotypes, mp_indices)

    def add_evidence_label(self):
        evidences  = list(set(self.store.objects(None, OBO.RO_0002558)))
        evidence_iris = list(map(lambda i:str(i), evidences))
        logger.info("Resolving iris; total:%d", len(evidence_iris))
        evidence_indices = lookup_es.find_entity_by_iris(evidence_iris, 'ECO')
        self.add_label(evidence_iris, evidence_indices)

    def add_label(self, iris, indices):
        for iri in iris:
            try:
                index = next(idx for idx in indices if idx['entity'] == iri)
                if index and index['valueset'] in ['MGI', 'NCBIGene']:
                    self.store.add((URIRef(iri), RDFS.label, Literal(index['label'][0] + '  ' + index['label'][1], datatype = XSD.string)))
                elif index:
                    self.store.add((URIRef(iri), RDFS.label, Literal(index['label'][0], datatype = XSD.string)))
                
            except StopIteration as e:
                logger.warning("Did not find label for:" + iri)
                continue

    def add_association(self, association):
        self.associationset.add(PHENO.association, association)
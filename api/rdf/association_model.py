

import uuid

from api.rdf.namespace import PHENO, OBO, PUBCHEM, MGI, ENTREZ_GENE, DECIPHER, OMIM, ORPHA, PMID, ISBN 
from rdflib.namespace import FOAF, DC, RDFS, DCTERMS
from rdflib import Graph, Literal, RDF, XSD, URIRef


def create_graph():
    store = Graph()
    store.bind("dc", DC)
    store.bind("dcterms", DCTERMS)
    store.bind("pheno", PHENO)
    store.bind("obo", OBO)
    store.bind("pubchem", PUBCHEM)
    store.bind("mgi", MGI)
    store.bind("gene", ENTREZ_GENE)
    return store

def add_association_provenance(store, association, creator=None, created_on=None, source=None):
    provenance = store.resource(str(PHENO.uri) + str(uuid.uuid4()))
    provenance.add(RDF.type, DCTERMS.ProvenanceStatement)
    if creator:
        provenance.add(DC.creator, Literal(creator, datatype=XSD.string))
    if created_on:
        provenance.add(DCTERMS.created, Literal(created_on, datatype=XSD.date))
    if source:
        if isinstance(source, str):
            provenance.add(DCTERMS.source, Literal(source))
        else:
            for item in source:
                provenance.add(DCTERMS.source, Literal(item))


    association.add(DC.provenance, provenance)
    return association

def create_phenotypic_association(store, subject, object):
    association = store.resource(str(PHENO.uri) + "association/" + str(uuid.uuid4()))
    association.add(RDF.type, RDF.Statement)
    association.add(RDF.subject, subject)
    association.add(RDF.predicate,OBO.RO_0002200)
    association.add(RDF.object, object)
    subject.add(OBO.RO_0002200, object)
    return association

def create_associationset(store, assoicationset, types=[]):
    associationset = store.resource(str(PHENO.uri) + "associationset/" + str(uuid.uuid4()))
    associationset.add(RDF.type, PHENO.AssociationSet)
    associationset.add(RDFS.label, Literal(assoicationset['name'], datatype=XSD.string))
    associationset.add(PHENO.download, Literal(assoicationset['download'], datatype=XSD.string))
    associationset.add(DC.description, Literal(assoicationset['description'], datatype=XSD.string))
    associationset.add(DCTERMS.source, Literal(assoicationset['url'], datatype=XSD.string))
    for type in assoicationset['includeTypes']:
        associationset.add(PHENO.includeTypes, store.resource(type))
    return associationset
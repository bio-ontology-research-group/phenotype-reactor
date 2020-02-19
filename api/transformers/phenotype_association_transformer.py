# Transforms phenotype association files to rdf files
from rdflib import Graph, Literal, BNode, RDF
from rdflib.namespace import FOAF, DC, ClosedNamespace, RDFS, DCTERMS
from rdflib.term import URIRef

from django.conf import settings

from pathlib import Path

import pandas as pd

import json
import uuid
import sys


DATA_FOLDER = getattr(settings, 'SOURCE_DATA_FOLDER', str(Path.home()) + '/data/phenodb')
TARGET_DATA_FOLDER = getattr(settings, 'TARGET_DATA_FOLDER', str(Path.home()) + '/data/phenodb')
FORMAT = getattr(settings, 'EXPORT_FORMAT', 'pretty-xml')

HPO_PIPELINE_BASE_URL = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/'
HPO_ANNO_URL = HPO_PIPELINE_BASE_URL + 'phenotype_annotation.tab'
HPO_ANNO_HPO_TEAM_URL = HPO_PIPELINE_BASE_URL + 'phenotype_annotation_hpoteam.tab'

print(DATA_FOLDER, FORMAT)

FORMAT_DIC = {
    'xml' : 'rdf', 'n3': 'n3', 'turtle': 'ttl', 'nt': 'nt', 'pretty-xml': 'rdf', 'trix': 'trix', 'trig': 'trig', 'nquads':'nquads'
}

PHENO = ClosedNamespace(
    uri=URIRef("http://phenodb.phenomebrowser.net/"),
    terms=[
        #Classes
        "Disease", "Drug", "Device", "Gene", "Genotype",
        "Phenotype", "Pathogen", "Provenance", "Association", "Metabolite",

        #Properties
        "ecNumber", "uniprotId", "url", "failedToContributeToCondition"
    ]
)

OBO = ClosedNamespace(
    uri=URIRef("http://purl.obolibrary.org/obo/"),
    terms=[
        #has evidence
        "RO_0002558",
        #has phenotype
        "RO_0002200",
        #phenotypic similarity evidence used in automatic assertion
        "ECO_0007824",
        #curator inference used in manual assertion (manually curated)
        "ECO_0000305",
        #similarity evidence used in automatic assertion
        "ECO_0000251",
        #computational evidence used in automatic assertion (text mining, lexical matching, based on NPMI value)
        "ECO_0007669"
    ]
)

PUBCHEM = ClosedNamespace(uri=URIRef("https://pubchem.ncbi.nlm.nih.gov/compound/"), terms=[])
MGI = ClosedNamespace(uri=URIRef("http://www.informatics.jax.org/marker/"), terms=[])
ENTREZ_GENE = ClosedNamespace(uri=URIRef("https://www.ncbi.nlm.nih.gov/gene/"), terms=[])

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
        provenance.add(DC.creator, Literal(creator))
    if created_on:
        provenance.add(DCTERMS.created, Literal(created_on))
    if source:
        provenance.add(DCTERMS.source, Literal(source))

    association.add(DC.provenance, provenance)
    return association

def create_phenotypic_association(store, subject, object):
    association = store.resource(str(PHENO.uri) + str(uuid.uuid4()))
    association.add(RDF.type, RDF.Statement)
    association.add(RDF.subject, subject)
    association.add(RDF.predicate,OBO.RO_0002200)
    association.add(RDF.object, object)
    return association

def transform_disease2phenotype():
    store = create_graph()
    filePath='{folder}/doid_phenotypes_sara.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep='\t', names=['disease', 'phenotype']) 
    df.phenotype = df.phenotype.replace(regex=[':'], value='_')
    df.disease = df.disease.replace(regex=[':'], value='_')
    print(df.head())
    
    for index, row in df.iterrows():
        disease = store.resource(str(OBO.uri) + row.disease)
        disease.add(RDF.type, PHENO.Disease)
        phenotype = store.resource(str(OBO.uri) + row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(store, disease, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(store, association, creator='Sara Althubaiti',
            source='https://www.ncbi.nlm.nih.gov/pubmed/30809638')
    

    store.serialize('{folder}/disease2phenotype.{extension}'.format(folder=TARGET_DATA_FOLDER, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_drug2phenotype():
    store = create_graph()
    filePath='{folder}/drug_phenotypes_sara.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep=' ', names=['drug', 'phenotype']) 
    df.phenotype = df.phenotype.replace(regex=['<'], value='').replace(regex=['>'], value='')
    df.drug = df.drug.replace(regex=['CID'], value='')
    print(df.head())
    
    for index, row in df.iterrows():
        drug = store.resource(str(PUBCHEM.uri) + row.drug)
        drug.add(RDF.type, PHENO.Drug)
        phenotype = store.resource(row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(store, drug, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(store, association, creator='Sara Althubaiti', created_on='2019-03-12',
         source="https://www.ncbi.nlm.nih.gov/pubmed/20087340")

    store.serialize('{folder}/drug2phenotype.{extension}'.format(folder=TARGET_DATA_FOLDER, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_gene2phenotype_text_mined():
    store = create_graph()
    filePath='{folder}/genephenotypes_textmined_senay.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep='\t', names=['mgi', 'entrez_gene',  'phenotype', 'score']) 
    df.mgi = df.mgi.astype(str).replace(regex=['nan'], value='')
    df[['gene1', 'gene2']] = df.entrez_gene.str.split("_#_", expand = True)
    print(df.head())
    
    split_count=1
    source = 'https://www.ncbi.nlm.nih.gov/pubmed/30809638'
    for index, row in df.iterrows():
        # print(row.mgi, row.phenotype, row.gene1, row.gene2)
        phenotype = store.resource(str(OBO.uri) + row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        
        if row.mgi.strip():
            mgi = store.resource(str(MGI.uri) + row.mgi.strip())
            mgi.add(RDF.type, PHENO.Gene)
            association = create_phenotypic_association(store, mgi, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(store, association, creator='Senay Kafkas', 
                created_on='2019-01-06', source=source)

        if row.gene1:
            gene = store.resource(str(ENTREZ_GENE.uri) + row.gene1.strip())
            gene.add(RDF.type, PHENO.Gene)
            association = create_phenotypic_association(store, gene, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(store, association, creator='Senay Kafkas', 
                created_on='2019-01-06', source=source)

        if row.gene2:
            gene = store.resource(str(ENTREZ_GENE.uri) + row.gene2.strip())
            gene.add(RDF.type, PHENO.Gene)
            association = create_phenotypic_association(store, gene, phenotype)
            association.add(OBO.RO_0002558, OBO.ECO_0007669)
            add_association_provenance(store, association, creator='Senay Kafkas', 
                created_on='2019-01-06', source=source)

        if index > 0 and index % 150000 == 0:
            store.serialize('{folder}/gene2phenotype_textmined-{split_count}.{extension}'.format(folder=TARGET_DATA_FOLDER, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
            print(len(store))
            store.remove((None, None, None))
            split_count += 1

    split_count += 1
    store.serialize('{folder}/gene2phenotype_textmined-{split_count}.{extension}'.format(folder=TARGET_DATA_FOLDER, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    store.remove((None, None, None))
    del df

def transform_pathogen2phenotype():
    store = create_graph()
    filePath='{folder}/pathogens_phenotypes_shenay.txt'.format(folder=DATA_FOLDER)
    df = pd.read_json(filePath) 
    print(df.head())
    
    for index, row in df.iterrows():
        pathogen = store.resource(row.TaxID)
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
            phenotypeRes = store.resource(phenotype['id'])
            phenotypeRes.add(RDF.type, PHENO.Phenotype)
            association = create_phenotypic_association(store, pathogen, phenotypeRes)
            for evidence in evidences:
                association.add(OBO.RO_0002558, evidence)

            add_association_provenance(store, association, creator='Senay Kafkas', 
                created_on='2019-06-03', source='https://www.nature.com/articles/s41597-019-0090-x')

    store.serialize('{folder}/pathogen2phenotype.{extension}'.format(folder=TARGET_DATA_FOLDER, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_mondo2phenotype_top50():
    store = create_graph()
    filePath='{folder}/mondo-pheno_shenay.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep='\t') 
    df.Phenotype_ID = df.Phenotype_ID.replace(regex=[':'], value='_')
    df.Mondo_ID = df.Mondo_ID.replace(regex=[':'], value='_')
    print(df.head())
    
    for index, row in df.iterrows():
        disease = store.resource(str(OBO.uri) + row.Mondo_ID)
        disease.add(RDF.type, PHENO.Disease)
        phenotype = store.resource(str(OBO.uri) + row.Phenotype_ID)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(store, disease, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(store, association, creator='Senay Kafkas',
         source='https://www.ncbi.nlm.nih.gov/pubmed/30809638')


    store.serialize('{folder}/mondo2phenotype_top50.{extension}'.format(folder=TARGET_DATA_FOLDER, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_predictive_gene2phenotype():
    store = create_graph()
    filePath='{folder}/deeppheno_maxat.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep='\t', names=['gene', 'phenotype', 'score']) 
    df.phenotype = df.phenotype.replace(regex=[':'], value='_')
    df.gene = df.gene.astype(str)
    print(df.head())
    
    split_count = 1
    for index, row in df.iterrows():
        gene = store.resource(str(ENTREZ_GENE.uri) + row.gene)
        gene.add(RDF.type, PHENO.Gene)
        phenotype = store.resource(str(OBO.uri) + row.phenotype)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(store, gene, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(store, association, creator='Maxat Kulmanov', 
            created_on='2019-10-20', source='https://www.nature.com/articles/s41597-019-0090-x')

        if index > 0 and index % 200000 == 0:
            store.serialize('{folder}/predictive_gene2phenotype-sm-{split_count}.{extension}'.format(folder=TARGET_DATA_FOLDER, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
            print(len(store))
            store.remove((None, None, None))
            split_count += 1

    store.serialize('{folder}/predictive_gene2phenotype-sm-{split_count}.{extension}'.format(folder=TARGET_DATA_FOLDER, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_metabolites2phenotype():
    store = create_graph()
    filePath='{folder}/metabolite_pheno_shenay.txt'.format(folder=DATA_FOLDER)
    df = pd.read_csv(filePath, sep='\t') 
    df.CHEBI_ID = df.CHEBI_ID.replace(regex=[':'], value='_')
    df.Phenotype_ID = df.Phenotype_ID.replace(regex=[':'], value='_')
    print(df.head())
    
    for index, row in df.iterrows():
        metabolite = store.resource(str(OBO.uri) + row.CHEBI_ID)
        metabolite.add(RDF.type, PHENO.Metabolite)
        phenotype = store.resource(str(OBO.uri) + row.Phenotype_ID)
        phenotype.add(RDF.type, PHENO.Phenotype)
        association = create_phenotypic_association(store, metabolite, phenotype)
        association.add(OBO.RO_0002558, OBO.ECO_0007669)
        add_association_provenance(store, association, creator='Senay Kafkas',
         source='https://www.ncbi.nlm.nih.gov/pubmed/30809638')
    

    store.serialize('{folder}/metabolite2phenotype.{extension}'.format(folder=TARGET_DATA_FOLDER, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def print_size(file):
    store = create_graph()
    filePath='{folder}/{file}'
    store.load(filePath)
    print(len(store))
# Transforms phenotype association files to rdf files
from rdflib import Graph, Literal, BNode, RDF
from rdflib.namespace import FOAF, DC, RDFS, DCTERMS

from api.rdf.namespace import PHENO, OBO, PUBCHEM, MGI, ENTREZ_GENE, DECIPHER, OMIM, ORPHA, PMID, ISBN
from django.conf import settings

from pathlib import Path

import pandas as pd

import json
import uuid
import sys
import os
import datetime


DATA_DIR = getattr(settings, 'SOURCE_DATA_DIR', str(Path.home()) + '/data/phenodb')
TARGET_DATA_DIR = getattr(settings, 'TARGET_DATA_DIR', str(Path.home()) + '/data/phenodb')
FORMAT = getattr(settings, 'EXPORT_FORMAT', 'pretty-xml')

HPO_PIPELINE_BASE_URL = 'http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/'
HPO_ANNO_URL = HPO_PIPELINE_BASE_URL + 'phenotype_annotation.tab'

print(DATA_DIR, FORMAT)

FORMAT_DIC = {
    'xml' : 'rdf', 'n3': 'n3', 'turtle': 'ttl', 'nt': 'nt', 'pretty-xml': 'rdf', 'trix': 'trix', 'trig': 'trig', 'nquads':'nquads'
}

def init():
    global TARGET_DATA_DIR
    os.chdir(TARGET_DATA_DIR)
    data_archive_dir =  'data-' + str(datetime.date.today())
    os.makedirs(data_archive_dir, exist_ok=True)
    TARGET_DATA_DIR = TARGET_DATA_DIR + '/' + data_archive_dir

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
        if isinstance(source, str):
            provenance.add(DCTERMS.source, Literal(source))
        else:
            for item in source:
                provenance.add(DCTERMS.source, Literal(item))


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
    filePath='{folder}/doid_phenotypes_sara.txt'.format(folder=DATA_DIR)
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
            source='https://pubmed.ncbi.nlm.nih.gov/30809638')
    

    store.serialize('{folder}/disease2phenotype.{extension}'.format(folder=TARGET_DATA_DIR, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_drug2phenotype():
    store = create_graph()
    filePath='{folder}/drug_phenotypes_sara.txt'.format(folder=DATA_DIR)
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
         source="https://pubmed.ncbi.nlm.nih.gov/20087340")

    store.serialize('{folder}/drug2phenotype.{extension}'.format(folder=TARGET_DATA_DIR, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_gene2phenotype_text_mined():
    store = create_graph()
    filePath='{folder}/genephenotypes_textmined_senay.txt'.format(folder=DATA_DIR)
    df = pd.read_csv(filePath, sep='\t', names=['mgi', 'entrez_gene',  'phenotype', 'score']) 
    df.mgi = df.mgi.astype(str).replace(regex=['nan'], value='')
    df[['gene1', 'gene2']] = df.entrez_gene.str.split("_#_", expand = True)
    print(df.head())
    
    split_count=1
    source = 'https://pubmed.ncbi.nlm.nih.gov/30809638'
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
            store.serialize('{folder}/gene2phenotype_textmined-{split_count}.{extension}'.format(folder=TARGET_DATA_DIR, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
            print(len(store))
            store.remove((None, None, None))
            split_count += 1

    split_count += 1
    store.serialize('{folder}/gene2phenotype_textmined-{split_count}.{extension}'.format(folder=TARGET_DATA_DIR, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    store.remove((None, None, None))
    del df

def transform_pathogen2phenotype():
    store = create_graph()
    filePath='{folder}/pathogens_phenotypes_shenay.txt'.format(folder=DATA_DIR)
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
                created_on='2019-06-03', source='https://pubmed.ncbi.nlm.nih.gov/31160594')

    store.serialize('{folder}/pathogen2phenotype.{extension}'.format(folder=TARGET_DATA_DIR, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_mondo2phenotype_top50():
    store = create_graph()
    filePath='{folder}/mondo-pheno_shenay.txt'.format(folder=DATA_DIR)
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
         source='https://pubmed.ncbi.nlm.nih.gov/30809638')


    store.serialize('{folder}/mondo2phenotype_top50.{extension}'.format(folder=TARGET_DATA_DIR, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_deeppheno_gene2phenotype():
    store = create_graph()
    filePath='{folder}/deeppheno_maxat.txt'.format(folder=DATA_DIR)
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
            created_on='2020-03-25', source='https://www.biorxiv.org/content/10.1101/839332v2')
        if index > 0 and index % 500000 == 0:
            store.serialize('{folder}/predictive_gene2phenotype-{split_count}.{extension}'.format(folder=TARGET_DATA_DIR, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
            print(len(store))
            store.remove((None, None, None))
            split_count += 1

    store.serialize('{folder}/predictive_gene2phenotype-{split_count}.{extension}'.format(folder=TARGET_DATA_DIR, split_count=split_count, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def transform_metabolites2phenotype():
    store = create_graph()
    filePath='{folder}/metabolite_pheno_shenay.txt'.format(folder=DATA_DIR)
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
         source='https://pubmed.ncbi.nlm.nih.gov/30809638')
    

    store.serialize('{folder}/metabolite2phenotype.{extension}'.format(folder=TARGET_DATA_DIR, extension=FORMAT_DIC[FORMAT]), format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

def print_size(file):
    store = create_graph()
    filePath='{folder}/{file}'
    store.load(filePath)
    print(len(store))
    

def transform_hpo_annotations(url, output_filename):
    store = create_graph()
    df = pd.read_csv(url, sep='\t') 
    df['HPO-ID'] = df['HPO-ID'].replace(regex=[':'], value='_')

    df['disease-identifier'] = df['disease-identifier'].astype(str)
    df['disease_iri'] = df[['#disease-db', 'disease-identifier']].apply(lambda x: ':'.join(x), axis=1)
    df['disease_iri'] = df['disease_iri'].replace(regex=['DECIPHER:'], value=DECIPHER.uri)
    df['disease_iri'] = df['disease_iri'].replace(regex=['OMIM:'], value=OMIM.uri)
    df['disease_iri'] = df['disease_iri'].replace(regex=['ORPHA:'], value=ORPHA.uri)

    df.reference = df.reference.replace(regex=['DECIPHER:'], value=DECIPHER.uri)
    df.reference = df.reference.replace(regex=['OMIM:'], value=OMIM.uri)
    df.reference = df.reference.replace(regex=['ORPHA:'], value=ORPHA.uri)
    df.reference = df.reference.replace(regex=['PMID:'], value=PMID.uri)
    df.reference = df.reference.replace(regex=['ISBN-13:'], value=ISBN.uri)
    df.reference = df.reference.replace(regex=['ISBN-10:'], value=ISBN.uri)
    df.reference = df.reference.astype(str).replace(regex=['nan'], value='')
    df.curators = df.curators.astype(str)
    print(df.head(), len(df.columns))

    pheno_disease_dict = {}
    for index, row in df.iterrows():
        phenotype = store.resource(str(OBO.uri) + row['HPO-ID'])
        phenotype.add(RDF.type, PHENO.Phenotype)

        diseaseRes = store.resource(row['disease_iri'])
        diseaseRes.add(RDF.type, PHENO.Disease)
        
        dict_key = row['HPO-ID'] + ":" + row['disease_iri']
        if dict_key not in pheno_disease_dict:
            association = create_phenotypic_association(store, diseaseRes, phenotype)

            evidence = None
            if 'IEA' in row['evidence-code']:
                evidence = OBO.ECO_0000501
            elif 'PCS' in row['evidence-code']:
                evidence = OBO.ECO_0006016
            elif 'ICS' in row['evidence-code']:
                evidence = OBO.ECO_0006018
            elif 'TAS' in row['evidence-code']:
                evidence = OBO.ECO_0000033

            association.add(OBO.RO_0002558, evidence)
            pheno_disease_dict[dict_key] = association
        else:
            association = pheno_disease_dict[dict_key]

        row.curators = row.curators.split(';')
        creator = []
        created_on = None

        for creator_field in row.curators:
            creator = (creator_field if creator_field.find('[') == -1 else creator_field[:creator_field.find('[')])
            created_on = (creator_field[creator_field.find('[') + 1: len(creator_field) - 1] if creator_field.find('[') > -1 else None)

        sources = ['https://pubmed.ncbi.nlm.nih.gov/30476213'] 
        for ref in row.reference.split(";"):
            if OMIM.uri in ref or DECIPHER.uri in ref or ORPHA.uri in ref:
                continue
            sources.append(ref)

        add_association_provenance(store, association, creator=creator, created_on=created_on,
        source=sources)

    store.serialize('{folder}/{filename}.{extension}'.format(
        folder=TARGET_DATA_DIR, filename=output_filename,  extension=FORMAT_DIC[FORMAT]), 
        format=FORMAT, max_depth=3)
    print(len(store))
    store.remove((None, None, None))
    del df

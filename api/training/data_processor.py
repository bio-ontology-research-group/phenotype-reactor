import tarfile
import os
import glob
import shutil
import subprocess
import csv
import logging
import api.archive.archive_ds as archive

from django.conf import settings

from api.rdf.namespace import OBO
from rdflib import Graph, RDF
from api.training.generate_graph import *
from api.training.data_ingestion.omim_genedisease import OMIMDiseaseGeneAssoc
from api.training.data_ingestion.patho_pathogendisease import PathoPathogenDiseaseAssoc

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path


logger = logging.getLogger(__name__)

ONTOLOGY_DIR = getattr(settings, 'ONTOLOGY_DIR', None)
KGE_DIR = getattr(settings, 'KGE_DIR', None)
TRAINING_SET_DIR = getattr(settings, 'TRAINING_SET_DIR', None)

def generate_nt(file):
    logger.info("Converting rdf file '{file}' to nt format".format(file=file))
    store = Graph()
    store.load(file)
    out_store = Graph()
    stmts = list(store.subjects(RDF.predicate, OBO.RO_0002200))
    phenotype_stmts = []
    for stmt in stmts:
        sub = store.value(stmt, RDF.subject)
        predicate = store.value(stmt, RDF.predicate)
        obj = store.value(stmt, RDF.object)
        out_store.add([sub, predicate, obj])

    out_store.serialize('{folder}/{filename}.nt'.format(folder=TRAINING_SET_DIR, filename=file), format='nt')
    out_store.remove((None, None, None))
    store.remove((None, None, None))

def rdf2nt(ds_path):
    files = [file for file in os.listdir(ds_path) if isfile(file)]
    
    if len(files) < 1:
        raise Exception("no file in dataset exists to process")

    for entry in files:
        if isfile(join(entry)):
            generate_nt(entry)
        

def process_dataset():
    file = archive.find_latest_file()
    file_path = join(settings.TARGET_DATA_DIR, file.full_name)
    if exists(file_path):
        logger.info("Extracting data archive...")
        ds_tar = tarfile.open(file_path)
        ds_tar.extractall(KGE_DIR)
        ds_tar.close()
    
    ds_dir = join(KGE_DIR, 'data-*')
    ds_path = glob.glob(ds_dir)[0]
    rdf2nt(ds_path)
    shutil.rmtree(ds_path)
    logger.info("Completed dataset preprocessing")

def process_testset():
    omimdisease_gene = OMIMDiseaseGeneAssoc()
    omimdisease_gene.fetch()
    omimdisease_gene.map()
    omimdisease_gene.write()

    pathogen_disease = PathoPathogenDiseaseAssoc()
    pathogen_disease.fetch()
    pathogen_disease.map()
    pathogen_disease.write()


def process_ontology():
    os.chdir('load')
    files = [file for file in os.listdir(ONTOLOGY_DIR)]
    for entry in files:
        logger.info("Processing ontology '%s'", entry)
        args = join(ONTOLOGY_DIR, entry) + ", elk," + TRAINING_SET_DIR
        logger.info("Running process ontology with arguments '%s'", args)
        process = subprocess.Popen("gradle processontology '-PcliArgs=" + args + "'", stdout=subprocess.PIPE, shell=True)
        for line in process.stdout:
            logger.info(line.strip())
    
    logger.info("Extracted axioms from ontologies")
    files = [file for file in os.listdir(TRAINING_SET_DIR) if isfile(join(TRAINING_SET_DIR, file)) and 'ls' in splitext(file)[1]]
    for entry in files:
        logger.info("Converting axioms for file '%s' to a graph", entry)

        with open(join(TRAINING_SET_DIR, entry), "r") as f:
            outFile = join(TRAINING_SET_DIR, entry + ".tsv")
            with open(outFile, 'w') as file:
                writer = csv.writer(file, delimiter='\t')

                for line in f.readlines():
                    result = convert_graph(line.strip())
                    if not result:
                        continue
                    
                    writer.writerows(result)
            
        logger.info("Finished converting axioms for file '%s' to a graph", entry)
        
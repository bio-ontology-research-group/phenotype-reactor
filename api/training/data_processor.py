import tarfile
import os
import glob
import shutil
import subprocess
import csv
import logging
import api.archive.archive_ds as archive
import requests
import re

from django.conf import settings

from api.rdf.namespace import OBO
from rdflib import Graph, RDF
from api.training.generate_graph import *
from api.training.data_ingestion.omim_genedisease import OMIMDiseaseGeneAssoc
from api.training.data_ingestion.patho_pathogendisease import PathoPathogenDiseaseAssoc
from api.training.data_ingestion.curated_disgenet import CuratedDisgenetAssoc

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

    out_store.serialize(f'{TRAINING_SET_DIR}/{os.path.basename(file)}.nt', format='nt')
    out_store.remove((None, None, None))
    store.remove((None, None, None))

def rdf2nt(ds_path): 
    files = [file for file in os.listdir(ds_path) if isfile(join(ds_path, file))]
    if len(files) < 1:
        raise Exception("no file in dataset exists to process")

    for entry in files:
        generate_nt(join(ds_path, entry))
        

def process_dataset():
    url = 'http://phenomebrowser.net/archive/latest'
    response = requests.get(url, stream=True)
    filename = None
    if response.status_code == 200:
        file_header = response.headers['content-disposition']
        filename = re.findall("filename=(.+)", file_header)[0]
        tar_path = join(KGE_DIR, filename)
        with open(tar_path, 'wb') as f:
            f.write(response.raw.read())

        fileobj = archive.populate_file_object(tar_path)
        ds_dir = fileobj.full_name.split('.')[0]
        if exists(tar_path):
            logger.info("Extracting data archive...%s | %s", tar_path, ds_dir)
            ds_tar = tarfile.open(tar_path)
            ds_tar.extractall(KGE_DIR)
            ds_tar.close()
        
        rdf2nt(ds_dir)
        shutil.rmtree(ds_dir)
        shutil.rmtree(tar_path)
        logger.info("Completed dataset preprocessing")
    else:
        logger.error("Unable to download file")

def process_testset():
    omimdisease_gene = OMIMDiseaseGeneAssoc()
    omimdisease_gene.fetch()
    omimdisease_gene.map()
    omimdisease_gene.write()

    pathogen_disease = PathoPathogenDiseaseAssoc()
    pathogen_disease.fetch()
    pathogen_disease.map()
    pathogen_disease.write()

    disgenet = CuratedDisgenetAssoc()
    disgenet.fetch()
    disgenet.map()
    disgenet.write()


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
                    
                    norm_result = []
                    for triple in result:
                        norm_triple = []
                        for item in triple:
                            norm_triple.append(item.replace("<", "").replace(">", ""))
                        norm_result.append(norm_triple)
                    writer.writerows(norm_result)
            
        logger.info("Finished converting axioms for file '%s' to a graph", entry)
        
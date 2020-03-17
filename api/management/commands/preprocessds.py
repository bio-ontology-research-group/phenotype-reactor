import signal
import logging
import datetime
import tarfile
import os
import glob
import shutil
import subprocess
import csv

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import api.archive.archive_ds as archive

from api.rdf.namespace import OBO
from rdflib import Graph, RDF
from api.training.generate_graph import *

from networkx.readwrite import json_graph

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path

import pykeen
import pykeen.constants as pkc

logger = logging.getLogger(__name__)
logging.getLogger('pykeen').setLevel(logging.INFO)

ONTOLOGY_DIR = getattr(settings, 'ONTOLOGY_DIR', None)
KGE_DIR = getattr(settings, 'KGE_DIR', None)
TRAINING_SET_DIR = getattr(settings, 'TRAINING_SET_DIR', None)

class Command(BaseCommand):
    help = 'Training kg data'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.processes = {}
        signal.signal(signal.SIGTERM, self.stop_subprocesses)
        signal.signal(signal.SIGINT, self.stop_subprocesses)
        signal.signal(signal.SIGQUIT, self.stop_subprocesses)

    def add_arguments(self, parser):
        parser.add_argument('-d', '--process_data', type=str, help='skipping data set preprocessing if already done', ) 
        parser.add_argument('-o', '--process_ontology', type=str, help='skipping data set preprocessing if already done', ) 
        parser.add_argument('-c', '--clean', type=str, help='skipping data set preprocessing if already done', ) 
    
    def stop_subprocesses(self, signum, frame):
        if self.proc.poll() is None:
            self.proc.kill()
        exit(0)

    
    def generate_nt(self, file):
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

    def rdf2nt(self, ds_path):
        files = [file for file in os.listdir(ds_path) if isfile(file)]
        
        if len(files) < 1:
            raise Exception("no file in dataset exists to process")

        for entry in files:
            if isfile(join(entry)):
                self.generate_nt(entry)

        

    def preprocess_dataset(self):
        file = archive.find_latest_file()
        file_path = join(settings.TARGET_DATA_DIR, file.full_name)
        if exists(file_path):
            logger.info("Extracting data archive...")
            ds_tar = tarfile.open(file_path)
            ds_tar.extractall(KGE_DIR)
            ds_tar.close()
        
        ds_dir = join(KGE_DIR, 'data-*')
        ds_path = glob.glob(ds_dir)[0]
        self.rdf2nt(ds_path)
        shutil.rmtree(ds_path)
        logger.info("Completed dataset preprocessing")

    
    def preprocess_ontology(self):
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
                        
                
                
    def handle(self, *args, **options):
        process_data = options['process_data']
        process_ontology = options['process_ontology']
        clean = options['clean']

        try:
            if clean and 'true' in clean:
                if exists(TRAINING_SET_DIR):
                    shutil.rmtree(TRAINING_SET_DIR)

                os.makedirs(TRAINING_SET_DIR)

            if process_data and 'true' in process_data:
                self.preprocess_dataset()
            elif process_ontology and 'true' in process_ontology:
                self.preprocess_ontology()
            else: 
                self.preprocess_ontology()
                self.preprocess_dataset()
            
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")
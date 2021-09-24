import signal
import logging
import os
import shutil

import api.training.data_processor as dp

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.rdf.namespace import OBO
from rdflib import Graph, RDF
from api.training.generate_graph import *

from networkx.readwrite import json_graph

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path

logger = logging.getLogger(__name__)

ONTOLOGY_DIR = getattr(settings, 'ONTOLOGY_DIR', None)
TRAINING_SET_DIR = getattr(settings, 'TRAINING_SET_DIR', None)
TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class Command(BaseCommand):
    help = 'Training kg data'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.processes = {}
        signal.signal(signal.SIGTERM, self.stop_subprocesses)
        signal.signal(signal.SIGINT, self.stop_subprocesses)
        signal.signal(signal.SIGQUIT, self.stop_subprocesses)

    def add_arguments(self, parser):
        parser.add_argument('-d', '--process_data', type=str, help='data set preprocessing if already done', ) 
        parser.add_argument('-o', '--process_ontology', type=str, help='data set preprocessing if already done', ) 
        parser.add_argument('-t', '--process_testset', type=str, help='test set preprocessing if already done', ) 
        parser.add_argument('-c', '--clean', type=str, help='clean directory before data set preprocessing', )
        parser.add_argument('-od', '--ontology_subdirectory', type=str, default='', help='directory in ontology archive directory', )  
    
    def stop_subprocesses(self, signum, frame):
        if self.proc.poll() is None:
            self.proc.kill()
        exit(0)             
                
    def handle(self, *args, **options):
        process_data = options['process_data']
        process_ontology = options['process_ontology']
        process_testset = options['process_testset']
        clean = options['clean']
        ontology_subdirectory = options['ontology_subdirectory']

        try:
            if clean and 'true' in clean:
                if exists(TRAINING_SET_DIR):
                    shutil.rmtree(TRAINING_SET_DIR)

                logger.info("creating directory for training data")
                os.makedirs(TRAINING_SET_DIR)

                if exists(TEST_SET_DIR):
                    shutil.rmtree(TEST_SET_DIR)

                logger.info("creating directory for test data")
                os.makedirs(TEST_SET_DIR)

            if process_data and 'true' in process_data:
                dp.process_dataset()
            elif process_ontology and 'true' in process_ontology:
                dp.process_ontology(ontology_subdirectory)
            elif process_testset and 'true' in process_testset:
                dp.process_testset()
            else: 
                dp.process_ontology()
                dp.process_dataset()
            
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")
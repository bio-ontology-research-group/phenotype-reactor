import signal
import logging

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
                dp.process_dataset()
            elif process_ontology and 'true' in process_ontology:
                dp.process_ontology()
            else: 
                dp.process_ontology()
                dp.process_dataset()
            
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")
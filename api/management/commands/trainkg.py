import signal
import logging
import datetime
import tarfile
import os
import glob
import shutil

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import api.archive.archive_ds as archive

from api.rdf.namespace import OBO
from rdflib import Graph, RDF

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path

import pykeen
import pykeen.constants as pkc

logger = logging.getLogger(__name__)
logging.getLogger('pykeen').setLevel(logging.INFO)


RDF_DATA_ARCHIVE_DIR = getattr(settings, 'RDF_DATA_ARCHIVE_DIR', None)
KGE_DIR = getattr(settings, 'KGE_DIR', None)
TRAINING_SET_DIR = join(KGE_DIR, 'trainingset')
TEST_SET_FILE = join(TRAINING_SET_DIR, 'testset.nt')

class Command(BaseCommand):
    help = 'Training kg data'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.processes = {}
        signal.signal(signal.SIGTERM, self.stop_subprocesses)
        signal.signal(signal.SIGINT, self.stop_subprocesses)
        signal.signal(signal.SIGQUIT, self.stop_subprocesses)

    def add_arguments(self, parser):
        parser.add_argument('-l', '--learning_rate', type=str, help='learning rate for embeddings', )
        parser.add_argument('-e', '--num_epochs', type=str, help='number of epochs or iterations', )
        parser.add_argument('-d', '--embedding_dim', type=str, help='number of embedding dimensions', )
        parser.add_argument('-b', '--batch_size', type=str, help='batch size', ) 
        parser.add_argument('-r', '--device', type=str, help='preferred device', ) 
    
    def stop_subprocesses(self, signum, frame):
        if self.proc.poll() is None:
            self.proc.kill()
        exit(0)

                
    def handle(self, *args, **options):
        learning_rate = options['learning_rate']
        num_epochs = options['num_epochs']
        embedding_dim = options['embedding_dim']
        batch_size = options['batch_size']
        device = options['device']

        training_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('nt' in splitext(file)[1] or 'tsv' in splitext(file)[1])]
        try: 
            config = dict()
            config[pkc.TRAINING_SET_PATH] = training_files
            config[pkc.EXECUTION_MODE] = pkc.TRAINING_MODE
            config[pkc.KG_EMBEDDING_MODEL_NAME] = pkc.TRANS_E_NAME
            config[pkc.SEED] = 0
            config[pkc.LEARNING_RATE] = float(learning_rate) if learning_rate else 0.01
            config[pkc.NUM_EPOCHS] = int(num_epochs) if num_epochs else 10
            config[pkc.BATCH_SIZE] = int(batch_size) if batch_size else 64
            config[pkc.PREFERRED_DEVICE] = device if device else pkc.GPU
            config[pkc.EMBEDDING_DIM] = int(embedding_dim) if embedding_dim else 50
            config[pkc.SCORING_FUNCTION_NORM] = 1  # corresponds to L1
            config[pkc.NORM_FOR_NORMALIZATION_OF_ENTITIES] = 2  # corresponds to L2
            config[pkc.MARGIN_LOSS] = 1  # corresponds to L1
            
            logger.info("Starting training dataset with settings:" + str(config))
            
            os.chdir(KGE_DIR)
            results = pykeen.run(
                config=config,
                output_directory=KGE_DIR,
            )

            print('Keys:', *sorted(results.results.keys()), sep='\n  ')
            logger.info(results.trained_model)
            logger.info(results.losses)
                    
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")
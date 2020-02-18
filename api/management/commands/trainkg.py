from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from os import listdir
from os.path import isfile, join, splitext
from pathlib import Path

import api.rdfox as rdfox

import pykeen
import pykeen.constants as pkc

import signal
import logging
import datetime


logger = logging.getLogger(__name__)


RDF_DATA_ARCHIVE_FOLDER = getattr(settings, 'RDF_DATA_ARCHIVE_FOLDER', None)
KGE_FOLDER = getattr(settings, 'KGE_FOLDER', None)

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

        if RDF_DATA_ARCHIVE_FOLDER is None or not RDF_DATA_ARCHIVE_FOLDER:
            raise Exception("configuration property 'archive.dir' is required")
        if KGE_FOLDER is None or not KGE_FOLDER:
            raise Exception("configuration property 'kge.dir' is required")

        try: 
            config = dict()
            config[pkc.TRAINING_SET_PATH] = join(RDF_DATA_ARCHIVE_FOLDER, 'bk-2020-02-03T12:50.nt')
            config[pkc.EXECUTION_MODE] = pkc.TRAINING_MODE
            config[pkc.KG_EMBEDDING_MODEL_NAME] = pkc.TRANS_E_NAME
            config[pkc.SEED] = 0
            config[pkc.LEARNING_RATE] = float(learning_rate) if learning_rate else 0.01
            config[pkc.NUM_EPOCHS] = int(num_epochs) if num_epochs else 10
            config[pkc.BATCH_SIZE] = int(embedding_dim) if embedding_dim else 64
            config[pkc.PREFERRED_DEVICE] = device if device else pkc.GPU
            config[pkc.EMBEDDING_DIM] = int(batch_size) if embedding_dim else 50
            config[pkc.SCORING_FUNCTION_NORM] = 1  # corresponds to L1
            config[pkc.NORM_FOR_NORMALIZATION_OF_ENTITIES] = 2  # corresponds to L2
            config[pkc.MARGIN_LOSS] = 1  # corresponds to L1
            
            logger.info(config)
            
            results = pykeen.run(
                config=config,
                output_directory=KGE_FOLDER,
            )

            print('Keys:', *sorted(results.results.keys()), sep='\n  ')
            logger.info(results.trained_model)
            logger.info(results.losses)
                    
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")
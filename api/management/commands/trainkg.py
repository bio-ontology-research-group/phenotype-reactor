import signal
import logging
import os
import shutil
import csv
import json
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from rdflib.namespace import split_uri

from os import listdir
from os.path import isfile, join, splitext, exists
from pathlib import Path

import pykeen
import pykeen.constants as pkc 


logger = logging.getLogger(__name__)
logging.getLogger('pykeen').setLevel(logging.INFO)

KGE_DIR = getattr(settings, 'KGE_DIR', None)
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
        parser.add_argument('-l', '--learning_rate', type=str, help='learning rate for embeddings', )
        parser.add_argument('-e', '--num_epochs', type=str, help='number of epochs or iterations', )
        parser.add_argument('-d', '--embedding_dim', type=str, help='number of embedding dimensions', )
        parser.add_argument('-b', '--batch_size', type=str, help='batch size', ) 
        parser.add_argument('-r', '--device', type=str, help='preferred device', ) 
        parser.add_argument('-tn', '--testset_name', type=str, help='testset name', ) 
    
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
        testset_name = options['testset_name']

        training_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('nt' in splitext(file)[1] or 'tsv' in splitext(file)[1])]
        try: 
            config = dict()
            config[pkc.TRAINING_SET_PATH] = training_files
            config[pkc.TEST_SET_PATH] = join(TEST_SET_DIR, testset_name + '.tsv')
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
            config[pkc.FILTER_NEG_TRIPLES] = True,
            
            logger.info("Starting training dataset with settings:" + str(config))
            
            out_dir = join(KGE_DIR, pkc.TRANS_E_NAME + '-' + testset_name + '-' + str(datetime.date.today())
            os.makedirs(out_dir)
            os.chdir(out_dir)
            results = pykeen.run(
                config=config,
                output_directory=out_dir,
            )

            print('Keys:', *sorted(results.results.keys()), sep='\n  ')
            logger.info(results.trained_model)
            logger.info(results.losses)

            self.generate_bio2vec_frmt(out_dir)
                    
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")


    def generate_bio2vec_frmt(self, out_dir): 
        logger.info("Started generating bio2vec dataset file")

        entity_emb_file = 'entities_to_embeddings.json'
        with open(join(out_dir, entity_emb_file), "r") as f:
                entity_emb = json.load(f)

                sep = ','
                outFile = join(out_dir, "entities_to_embeddings.bio2vec.tsv")
                with open(outFile, 'w') as file:
                    writer = csv.writer(file, delimiter='\t')

                    for key in entity_emb:
                        local_name = ''
                        try:
                            uri = key[1:len(key) -1]
                            local_name = split_uri(uri)[1]
                        except Exception:
                            pass

                        row =[key, local_name, '', '', 'entity', sep.join(map(str, entity_emb[key]))]
                        writer.writerow(row)

        logger.info("Finished generating bio2vec dataset file")
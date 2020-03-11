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
        parser.add_argument('-sp', '--skip_preprocessing', type=str, help='skipping data set preprocessing if already done', ) 
        parser.add_argument('-t', '--test', type=str, help='For training with test set', ) 
    
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

    def rdf2nt(self, ds_path, test):
        os.chdir(ds_path)
        files = [file for file in os.listdir('.') if isfile(file)]
        
        if len(files) < 1:
            raise Exception("no file in dataset exists to process")

        if exists(TRAINING_SET_DIR):
            shutil.rmtree(TRAINING_SET_DIR)

        os.makedirs(TRAINING_SET_DIR)
        for entry in files:
            if isfile(join(entry)):
                self.generate_nt(entry)

        

    def preprocess_dataset(self, test=False):
        file = archive.find_latest_file()
        file_path = join(settings.TARGET_DATA_DIR, file.full_name)
        if exists(file_path):
            logger.info("Extracting data archive...")
            ds_tar = tarfile.open(file_path)
            ds_tar.extractall(KGE_DIR)
            ds_tar.close()
        
        ds_dir = join(KGE_DIR, 'data-*')
        ds_path = glob.glob(ds_dir)[0]
        self.rdf2nt(ds_path, test)
        shutil.rmtree(ds_path)
        logger.info("Completed dataset preprocessing")

                
    def handle(self, *args, **options):
        learning_rate = options['learning_rate']
        num_epochs = options['num_epochs']
        embedding_dim = options['embedding_dim']
        batch_size = options['batch_size']
        device = options['device']
        skip_preprocessing = options['skip_preprocessing']

        if RDF_DATA_ARCHIVE_DIR is None or not RDF_DATA_ARCHIVE_DIR:
            raise Exception("configuration property 'archive.dir' is required")
        if KGE_DIR is None or not KGE_DIR:
            raise Exception("configuration property 'kge.dir' is required")
        
        if not skip_preprocessing or (skip_preprocessing and 'true' not in skip_preprocessing):
            self.preprocess_dataset()

        training_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and TEST_SET_FILE not in file]
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
import signal
import logging
import os
import shutil
import csv
import json
import datetime
import pickle
import gensim

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from rdflib.namespace import split_uri

from os import listdir
from os.path import isfile, join, splitext, exists
from api.training.generate_graph import *
from api.training.dl2vec.compute_vector import *

logger = logging.getLogger(__name__)
logging.getLogger('pykeen').setLevel(logging.INFO)

KGE_DIR = getattr(settings, 'KGE_DIR', None)
TRAINING_SET_DIR = getattr(settings, 'TRAINING_SET_DIR', None)
TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class Command(BaseCommand):
    help = 'Training kg data using dl2vec'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', type=str, default='sg', help='Preferred word2vec architecture, sg or cbow', )
        parser.add_argument('-d', '--embedding_dim', type=int, default=50, help='Computed vector dimensions', )
        parser.add_argument('-e', '--num_epochs', type=int, default=30, help='Number of epochs for the experiment', )
        parser.add_argument('-w', '--workers', type=int, default=30, help='Number of worker threads while training', )
        parser.add_argument('-tn', '--testset_name', type=str, default='', help='testset name', ) 
    
    def handle(self, *args, **options):
        model = options['model']
        embedding_dim = options['embedding_dim']
        num_epochs = options['num_epochs']
        workers = options['workers']
        testset_name = options['testset_name']
        
        try:
            annontation_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('nt' in splitext(file)[1])]
            axiom_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('.ls' in splitext(file)[1])]
            
            outdir = join(KGE_DIR, 'dl2vec' + '-' + testset_name + '-' + str(datetime.date.today()))
            os.makedirs(outdir, exist_ok=True)
            os.chdir(outdir)

            config = {
                'trainingset': annontation_files,
                'axiom_files': axiom_files,
                'model': model,
                'output_directory': outdir,
                'num_epochs': num_epochs,
                'embedding_dim': embedding_dim,
                'workers': workers
            }
            logger.info("Starting training dataset with settings:" + str(config))
            (graph, node_set) = generate_graph_and_annontation_nodes(annontation_files, axiom_files)
            model = gene_node_vector(graph, node_set, config)
            self.generate_bio2vec_frmt(model, outdir)
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")


    def generate_bio2vec_frmt(self, model, outdir): 
        logger.info("Started generating bio2vec dataset file")

        entity_emb = model
        sep = ','
        outFile = join(outdir, "embeddings.bio2vec.tsv")
        with open(outFile, 'w') as file:
            writer = csv.writer(file, delimiter='\t')

            for key in entity_emb.wv.vocab:
                local_name = ''
                try:
                    uri = key[1:len(key) -1]
                    local_name = split_uri(uri)[1]
                except Exception:
                    pass

                row =[key, local_name, '', '', 'entity', sep.join(map(str, entity_emb[key]))]
                writer.writerow(row)

        logger.info("Finished generating bio2vec dataset file")
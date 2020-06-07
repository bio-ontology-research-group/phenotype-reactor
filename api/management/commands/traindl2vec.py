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
        parser.add_argument('-tn', '--testset_name', type=str, help='testset name', ) 
    
    def handle(self, *args, **options):
        model = options['model']
        testset_name = options['testset_name']
        
        try:
            annontation_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('nt' in splitext(file)[1])]
            axiom_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('.ls' in splitext(file)[1])]
            
            out_dir = join(KGE_DIR, 'dl2vec' + '-' + testset_name + '-' + str(datetime.date.today()))
            os.makedirs(out_dir, exist_ok=True)
            os.chdir(out_dir)

            config = {
                'trainingset': annontation_files,
                'axiom_files': axiom_files,
                'model': model,
                'output_directory': out_dir
            }
            logger.info("Starting training dataset with settings:" + str(config))
            (graph, node_set) = generate_graph_and_annontation_nodes(annontation_files, axiom_files)
            gene_node_vector(graph, node_set, out_dir)
            # self.generate_bio2vec_frmt(out_dir)
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
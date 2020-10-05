import signal
import logging
import os
import shutil
import csv
import json
import datetime
import pickle
import gensim
import subprocess
import traceback

import networkx as nx

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from rdflib.namespace import split_uri
from api.rdf.namespace import find_type

from os import listdir
from os.path import isfile, join, splitext, exists
from api.training.dl2vec.compute_vector import *
from api.training.generate_graph import *
from api.training.evaluator import *

logger = logging.getLogger(__name__)
logging.getLogger('pykeen').setLevel(logging.INFO)

KGE_DIR = getattr(settings, 'KGE_DIR', None)
TRAINING_SET_DIR = getattr(settings, 'TRAINING_SET_DIR', None)
TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class Command(BaseCommand):
    help = 'Training kg data using deepwalk + word2vec'

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', type=str, default='sg', help='Preferred word2vec architecture, sg or cbow', )
        parser.add_argument('-d', '--representation_size', type=int, default=256, help='Computed vector dimensions', )
        parser.add_argument('-w', '--workers', type=int, default=32, help='Number of worker threads while training', )
        parser.add_argument('-wl', '--walk_length', type=int, default=100, help='Random walk length', )
        parser.add_argument('-n', '--number_walks', type=int, default=20, help='Number of walks', )
        parser.add_argument('-s', '--window_size', type=int, default=10, help='Window size', )
        parser.add_argument('-ep', '--epochs', type=int, default=30, help='number of iterations', )
        parser.add_argument('-tn', '--testset_name', type=str, default='', help='testset name', ) 
        parser.add_argument('-e', '--exp_name', type=str, default='', help='experiment name', ) 
        parser.add_argument('-dg', '--directed', nargs='?', const=True, default=False, help='directed or undirected graph by default the graph is undirected', ) 
    
    def handle(self, *args, **options):
        model = options['model']
        representation_size = options['representation_size']
        workers = options['workers']
        walk_length = options['walk_length']
        number_walks = options['number_walks']
        window_size = options['window_size']
        testset_name = options['testset_name']
        directed = options['directed']
        exp_name = options['exp_name']
        epochs = options['epochs']

        try:
            annontation_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('nt' in splitext(file)[1])]
            axiom_files = [join(TRAINING_SET_DIR, file) for file in os.listdir(TRAINING_SET_DIR + '/.') if (file) and ('.ls' in splitext(file)[1])]

            outdir = join(KGE_DIR, 'word2vec' + '-' + testset_name + '-' + (exp_name + '-' if exp_name else '') + str(datetime.date.today())) 
            cwd = os.getcwd()
            os.makedirs(outdir, exist_ok=True)
            # os.chdir(outdir)

            config = {
                'trainingset': annontation_files,
                'axiom_files': axiom_files,
                'model': 'word2vec',
                'output_directory': outdir,
                'walk_length': walk_length,
                'number_walks': number_walks,
                'representation_size': representation_size,
                'epochs': epochs,
                'window_size': window_size,
                'workers': workers,
                'testset_name': testset_name,
                'directed': directed,
            }

            self.write_json(config, join(outdir, "config.json"))
            logger.info("Starting training dataset with settings:" + str(config))
            (graph, node_dict) = generate_deepwalk_graph(annontation_files, axiom_files)

            if directed:
                graph = graph.to_directed()
            
            edgelist_outfile = join(outdir, "kb.edgelist")
            nx.write_edgelist(graph, edgelist_outfile)

            self.write_nodes_file(node_dict, outdir)
            walkfile = join(outdir, "walkfile.txt")
            CMD = f'./deepwalk {edgelist_outfile} {walkfile} {number_walks} {walk_length} {workers}'
            process = subprocess.Popen(CMD, text=True, shell=True)
            if process.wait() != 0:
                exit(0)
            
            # node_file = open("nodes.json", "r") 
            # node_dict = json.load(node_file)
            model = compute_vector_with_word2vec(walkfile, representation_size, epochs, workers, outdir)
            # model = gensim.models.Word2Vec.load(join(outdir, "embeddings.pkl"))
            self.generate_bio2vec_frmt(model, node_dict, outdir)
            run_evaluation(outdir, join(TEST_SET_DIR, testset_name + '.tsv'), testset_name)
            logger.info("Finished training dataset")
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")

    def generate_bio2vec_frmt(self, model, node_dict, outdir): 
        logger.info("Started generating bio2vec dataset file")
        id2node_map = dict((v, k) for k, v in node_dict.items())

        entity_emb = model
        sep = ','
        outFile = join(outdir, "embeddings.bio2vec.tsv")
        with open(outFile, 'w') as file:
            writer = csv.writer(file, delimiter='\t')

            for key in entity_emb.wv.vocab:
                if not key.isdigit():
                    print("key not found:", key)
                    continue

                if int(key) not in id2node_map:
                    print("key not found:", key)
                    continue
                
                node = id2node_map[int(key)]
                local_name = ''
                entity_type = 'entity'
                try:
                    uri = node[1:len(node) -1]
                    entity_type = find_type(uri)
                    node = uri
                    local_name = split_uri(uri)[1]
                except Exception:
                    pass

                row =[node, local_name, '', '', entity_type, sep.join(map(str, entity_emb[key]))]
                writer.writerow(row)

        logger.info("Finished generating bio2vec dataset file")

    def write_nodes_file(self, node_dict, outdir):
        self.write_json(node_dict, join(outdir, "nodes.json"))

    def write_json(self, dictionary, file):
        json_file = open(file, "w")
        json.dump(dictionary, file, indent=4)
        json_file.close()

           
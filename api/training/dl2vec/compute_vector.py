from __future__ import print_function

import numpy as np
import random
import json
import sys
import os
import gensim

import networkx as nx
from networkx.readwrite import json_graph
import multiprocessing as mp
from threading import Lock
import pickle as pkl
from os.path import join


lock = Lock()

WALK_LEN=30
N_WALKS=100

global data_pairs
data_pairs = []



def run_random_walks(G, nodes, outdir, num_walks=N_WALKS):
    print("now we start random walk")

    pairs = []
    for count, node in enumerate(nodes):

        if G.degree(node) == 0:
            continue
        for i in range(num_walks):
            curr_node = node
            walk_accumulate=[]
            for j in range(WALK_LEN):
                next_node = random.choice(list(G.neighbors(curr_node)))

                type_nodes = G.edges[curr_node, next_node]["type"]

                if curr_node ==node:
                    walk_accumulate.append(curr_node)
                walk_accumulate.append(type_nodes)
                walk_accumulate.append(next_node)

                curr_node = next_node

            pairs.append(walk_accumulate)
        if count % 1000 == 0:
            print("Done walks for", count, "nodes")
    write_file(pairs, outdir)


def run_walk(nodes,G, outdir):
    global data_pairs

    number=5
    length = len(nodes) // number

    processes = [mp.Process(target=run_random_walks, args=(G, nodes[(index) * length:(index + 1) * length], outdir)) for index
                 in range(number-1)]
    processes.append(mp.Process(target=run_random_walks, args=(G, nodes[(number-1) * length:len(nodes) - 1], outdir)))

    for p in processes:
        p.start()
    for p in processes:
        p.join()



    print("finish the work here")




def write_file(pair, outdir):
    with lock:
        with open(join(outdir, "walks.txt"), "a") as fp:
            for p in pair:
                for sub_p in p:
                    fp.write(str(sub_p)+" ")
                fp.write("\n")


class iteration_callback(gensim.models.callbacks.CallbackAny2Vec):
    '''Callback to print loss after each epoch.'''

    def __init__(self, outdir):
        self.epoch = 0
        self.outdir = outdir

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()
        print('Loss after epoch {}: {}'.format(self.epoch, loss))
        with lock:
            with open(join(self.outdir, "losses.tsv"), "a") as fp:
                fp.write(str(self.epoch) + "\t" + str(loss) + "\n")
        self.epoch += 1

def gene_node_vector(graph, nodes_set, config):
    # nodes_set=set()
    # with open(entity_list,"r") as f:
    #     for line in f.readlines():
    #         data = line.strip().split()
    #         for da in data:
    #             nodes_set.add(da)
    outdir = config['output_directory']
    size = config['embedding_dim']
    epochs = config['num_epochs']
    workers = config['workers']
    nodes_G= [n for n in graph.nodes()]

    G = graph.subgraph(nodes_G)
    nodes= [n for n in nodes_set]
    run_walk(nodes, G, outdir)

    print("start to train the word2vec models")
    sentences=gensim.models.word2vec.LineSentence(join(outdir, "walks.txt"))
    model=gensim.models.Word2Vec(sentences,sg=1, min_count=1, size=size, window=10,iter=epochs,workers=workers, compute_loss=True, callbacks=[iteration_callback(outdir)])
    model.save(join(outdir, "embeddings.pkl"))
    return model

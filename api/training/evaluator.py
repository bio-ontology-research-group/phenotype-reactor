import pdb
import json
import random
import logging

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import auc

from os.path import isfile, join, splitext, exists


logger = logging.getLogger(__name__)

def negcum(rank_vec):
    rank_vec_cum = []
    prev = 0
    for x in rank_vec:
        if x == 0:
            x = x+1
            prev = prev + x
            rank_vec_cum.append(prev)
        else:
            rank_vec_cum.append(prev)
    rank_vec_cum = np.array(rank_vec_cum)
    return rank_vec_cum


def evaluate_curated_disgenet(outdir, test_file):
    df = pd.read_csv(join(outdir, "embeddings.bio2vec.tsv"), sep = '\t', names=['uri', 'label', 'syn', 'alt', 'type', 'vector'])
    df['vector'] = df['vector'].str.split(",")
    logger.info('head: %s', df.head())

    embds_dict = dict(zip(df['uri'],df['vector']))

    gene_embeddings = {}
    disease_embeddings = {}

    for key in embds_dict.keys(): 
        if 'https://www.ncbi.nlm.nih.gov/gene/' in key:
            gene_embeddings[key] = [float(i) for i in embds_dict[key]]
        if 'DOID' in key:
            disease_embeddings[key] = embds_dict[key]

    print("gene", len(gene_embeddings.keys()))
    print("disease", len(disease_embeddings.keys()))

    disease_gene_df = pd.read_csv(test_file, sep = '\t', names=['disease', 'relation', 'gene'])
    disease_genes = {}
    for index, row in disease_gene_df.iterrows():
        if row.disease in disease_genes:
            disease_genes[row.disease].append(row.gene)
        else:
            disease_genes[row.disease]=[row.gene]

    genes_vecs = np.array([vec for vec in gene_embeddings.values()])
    genes = list(gene_embeddings.keys())
    label_mat = {}
    
    for dis in disease_genes.keys():
        assoc_genes = disease_genes[dis]
        s1 = list(set(assoc_genes))
        s2 = set(genes)
        if set(s1).intersection(s2):
            disease_embed = list()
            if dis in disease_embeddings:
                disease_embed.append(disease_embeddings[dis])
                disease_embed = np.array(disease_embed, dtype='float32')

                sim_scores = cosine_similarity(genes_vecs,disease_embed)
                sim_scores = sim_scores.flatten()
                sorted_idx = np.argsort(sim_scores)[::-1]
                sort_gene = [genes[arg] for arg in sorted_idx]

                label_vec = [0]*len(sort_gene)
                for gene in set(s1):
                    if gene in sort_gene:
                        label_vec[sort_gene.index(gene)] = 1
                label_mat[dis] = label_vec

    array_tp = np.zeros((len(label_mat), len(genes)),dtype='float32')
    array_fp = np.zeros((len(label_mat), len(genes)), dtype = 'float32')

    for i,row in enumerate(label_mat.values()):
        elem = np.asarray(row, dtype='float32')
        tpcum = np.cumsum(elem)
        fpcum = negcum(elem)
        array_tp[i] = tpcum
        array_fp[i] = fpcum

    #compute fpr and tpr Rob's way 
    tpsum = np.sum(array_tp, axis = 0)
    fpsum = np.sum(array_fp, axis = 0)
    tpr_r = tpsum/max(tpsum)
    fpr_r = fpsum/max(fpsum)

    auc_data2 = np.c_[fpr_r, tpr_r]

    print('Number of Disease: {}'.format(len(label_mat)))
    print('Number of genes: {}'.format(len(genes)))
    print('auc:  {}'.format(auc(fpr_r, tpr_r)))

    np.savetxt(join(outdir, 'evaluation.txt'), auc_data2, fmt = "%s")

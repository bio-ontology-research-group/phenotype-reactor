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

def run_evaluation(outdir, test_file, testset_name):
    if "CuratedDisgenetAssociation" in test_file:
        evaluate_curated_disgenet(outdir, test_file, testset_name)
    elif "PathoPathogenDiseaseAssociations" in test_file:
        evaluate_pathodisassoc(outdir, test_file, testset_name)
    elif "OmimDiseaseGeneAssociations" in test_file:
        evaluate_omimdisgene(outdir, test_file, testset_name)


def evaluate_curated_disgenet(outdir, test_file, testset_name):
    embds_dict = get_embeddings(outdir)
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

    (auc_data2, auc) = evaluate(disease_genes, disease_embeddings, gene_embeddings)
    np.savetxt(join(outdir, testset_name + '_evaluation.txt'), auc_data2, fmt = "%s")


def evaluate_pathodisassoc(outdir, test_file, testset_name):
    embds_dict = get_embeddings(outdir)
    disease_embeddings = {}
    pathogen_embeddings = {}

    for key in embds_dict.keys(): 
        if 'DOID' in key:
            disease_embeddings[key] = [float(i) for i in embds_dict[key]]
        if 'NCBITaxon' in key:
            pathogen_embeddings[key] = embds_dict[key]

    print("disease", len(disease_embeddings.keys()))
    print("pathogen", len(pathogen_embeddings.keys()))

    pathogen_disease_df = pd.read_csv(test_file, sep = '\t', names=['pathogen', 'relation', 'disease'])
    pathogen_disease = {}
    for index, row in pathogen_disease_df.iterrows():
        if row.disease in pathogen_disease:
            pathogen_disease[row.pathogen].append(row.disease)
        else:
            pathogen_disease[row.pathogen]=[row.disease]

    (auc_data2, auc) = evaluate(pathogen_disease, pathogen_embeddings, disease_embeddings)
    np.savetxt(join(outdir, testset_name + '_evaluation.txt'), auc_data2, fmt = "%s")

def evaluate_omimdisgene(outdir, test_file, testset_name):
    embds_dict = get_embeddings(outdir)
    gene_embeddings = {}
    disease_embeddings = {}

    for key in embds_dict.keys(): 
        if 'https://www.ncbi.nlm.nih.gov/gene/' in key:
            gene_embeddings[key] = [float(i) for i in embds_dict[key]]
        if 'https://omim.org/entry/' in key:
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

    (auc_data2, auc) = evaluate(disease_genes, disease_embeddings, gene_embeddings)
    np.savetxt(join(outdir, testset_name + '_evaluation.txt'), auc_data2, fmt = "%s")

def get_embeddings(outdir):
    df = pd.read_csv(join(outdir, "embeddings.bio2vec.tsv"), sep = '\t', names=['uri', 'label', 'syn', 'alt', 'type', 'vector'])
    df['vector'] = df['vector'].str.split(",")
    logger.info('head: %s', df.head())

    return dict(zip(df['uri'],df['vector']))
   
def evaluate(test_associations, src_concept_embeddings, tgt_concept_embeddings):
    tgt_concept_vecs = np.array([vec for vec in tgt_concept_embeddings.values()])
    tgt_concepts = list(tgt_concept_embeddings.keys())
    label_mat = {}

    for src_concept in test_associations.keys():
        assoc_src_concepts = test_associations[src_concept]
        s1 = list(set(assoc_src_concepts))
        s2 = set(tgt_concepts)
        if set(s1).intersection(s2):
            src_embed = list()
            if src_concept in src_concept_embeddings:
                src_embed.append(src_concept_embeddings[src_concept])
                src_embed = np.array(src_embed, dtype='float32')

                sim_scores = cosine_similarity(tgt_concept_vecs,src_embed)
                sim_scores = sim_scores.flatten()
                sorted_idx = np.argsort(sim_scores)[::-1]
                sort_tgt_concepts = [tgt_concepts[arg] for arg in sorted_idx]

                label_vec = [0]*len(sort_tgt_concepts)
                for tgt_concept in set(s1):
                    if tgt_concept in sort_tgt_concepts:
                        label_vec[sort_tgt_concepts.index(tgt_concept)] = 1
                label_mat[src_concept] = label_vec

    array_tp = np.zeros((len(label_mat), len(tgt_concepts)),dtype='float32')
    array_fp = np.zeros((len(label_mat), len(tgt_concepts)), dtype = 'float32')

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

    print('Number of Source Concepts: {}'.format(len(label_mat)))
    print('Number of Target Concepts: {}'.format(len(tgt_concepts)))
    print('auc:  {}'.format(auc(fpr_r, tpr_r)))

    return (auc_data2, auc)


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

from django.core.management.base import BaseCommand, CommandError

import api.transformers.phenotype_association_transformer as transformer
import api.archive.archive_ds as archive

import signal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Started transforming data to rdf'

    def add_arguments(self, parser):
        pass
                
    def handle(self, *args, **options):
        logger.info("Starting transforming source files to rdf")
        transformer.init()
        transformer.transform_disease2phenotype()
        transformer.transform_drug2phenotype()
        transformer.transform_gene2phenotype_text_mined()
        transformer.transform_pathogen2phenotype()
        transformer.transform_mondo2phenotype_top50()
        transformer.transform_predictive_gene2phenotype()
        transformer.transform_metabolites2phenotype()
        transformer.transform_hpo_annotations(transformer.HPO_ANNO_URL, 'disease2phenotype_hpo')
        archive.archive()
from django.core.management.base import BaseCommand, CommandError

import api.phenotype_association_transformer as transformer

import signal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Started transforming data to rdf'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.processes = {}
        signal.signal(signal.SIGTERM, self.stop_subprocesses)
        signal.signal(signal.SIGINT, self.stop_subprocesses)
        signal.signal(signal.SIGQUIT, self.stop_subprocesses)

    def add_arguments(self, parser):
        pass
    
    def stop_subprocesses(self, signum, frame):
        if self.proc.poll() is None:
            self.proc.kill()
        exit(0)
                
    def handle(self, *args, **options):
        transformer.transform_disease2phenotype()
        transformer.transform_drug2phenotype()
        transformer.transform_gene2phenotype_text_mined()
        transformer.transform_pathogen2phenotype()
        transformer.transform_mondo2phenotype_top50()
        transformer.transform_predictive_gene2phenotype()
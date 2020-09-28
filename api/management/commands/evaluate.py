import signal
import logging
import os
import shutil
import datetime
import subprocess
import traceback

import networkx as nx

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.training.evaluator import *

logger = logging.getLogger(__name__)

TEST_SET_DIR = getattr(settings, 'TEST_SET_DIR', None)

class Command(BaseCommand):
    help = 'Evaluating the model'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--testset', type=str, help='Testset name', )
        parser.add_argument('-e', '--embbeddingsdir', type=str, help='embeddings file directory', )
    
    def handle(self, *args, **options):
        testset = options['testset']
        embbeddingsdir = options['embbeddingsdir']

        if not testset:
            raise Exception("testset name is required")
        if not embbeddingsdir:
            raise Exception("embedding file directory name is required")

        try:
            run_evaluation(embbeddingsdir, join(TEST_SET_DIR, testset + '.tsv'), testset)
        except Exception as e:
            logger.exception("message")
        except RuntimeError:
            logger.exception("message")

     
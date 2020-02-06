from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from os import listdir
from os.path import isfile, join, splitext
from pathlib import Path

import api.rdfox as rdfox
import api.archive.archive_ds as archive

import signal
import logging

logger = logging.getLogger(__name__)

DATA_FOLDER = getattr(settings, 'RDF_DATA_FOLDER', str(Path.home()) + '/data/phenodb')

class Command(BaseCommand):
    help = 'Started loading rdf data'

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
        try:
            logging.info("Cleaning data store")
            rdfox.clean()
            logging.info("Started loading rdf data")
            rdf_files = [ifile for ifile in listdir(DATA_FOLDER) if (isfile(join(DATA_FOLDER, ifile)) and splitext(ifile)[1] == '.ttl')]

            for rdf_file in rdf_files:
                logging.info("Loading '{filename}' into store".format(filename=rdf_file))
                with open(join(DATA_FOLDER, rdf_file), 'r') as file:  
                    rdfox.upload(file.read()) 

            archive.archive()
        except Exception as e:
            logger.exception("message")
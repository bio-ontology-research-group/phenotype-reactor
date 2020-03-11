import time
import signal
import logging

from django.core.management.base import BaseCommand, CommandError

from api.lookup.ingest.valuesets import * 
from api.lookup.ingest.source import Source 
from api.lookup.ingest.decipher_hpo import DecipherValueset
from api.lookup.ingest.pubchem_sider import PubchemValueset
from api.lookup.ingest.mgi import MGIValueset
from api.lookup.ingest.omim import OMIMValueset
from api.lookup.ingest.ncbi_gene import NCBIGeneValueset

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
        logger.info("Starting indexing data")
        start_index = time.perf_counter()
        self.index(HP())
        self.index(MP())
        self.index(ORDO())
        self.index(NCBITAXON())
        self.index(DOID())
        self.index(MONDO())
        self.index(CHEBI())

    def index(self, valueset: Source):
        logger.info("Starting indexing %s", valueset.get_name())
        start_index = time.perf_counter()
        valueset.fetch()
        valueset.map()
        valueset.write()
        logger.info("Indexing time: %d sec", time.perf_counter() - start_index)
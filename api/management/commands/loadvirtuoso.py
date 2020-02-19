from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import signal
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

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
        os.chdir('load')
        process = subprocess.Popen('gradle runScript', stdout=subprocess.PIPE, shell=True)
        for line in process.stdout:
            logger.info(line.strip())

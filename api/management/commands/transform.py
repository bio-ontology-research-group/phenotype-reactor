import signal
import logging
import time
import datetime
import os

from django.core.management.base import BaseCommand, CommandError

from api.transformers.pathogen_pheno_ds import PathogenPhenoDS
from api.transformers.patho_disease_pheno_ds import PathoDiseasePhenoDS
from api.transformers.mondo_disease_pheno_ds import MondoDiseasePhenoDS
from api.transformers.deepheno_gene_pheno_ds import DeepphenoGenePhenoDS
from api.transformers.metabolite_pheno_ds import MetabolitePhenoDS
from api.transformers.textmined_gene_pheno_ds import TextminedhenoGenePhenoDS
from api.transformers.doid_disease_pheno_ds import DOIDDiseasePhenoDS
from api.transformers.drug_pheno_ds import DrugPhenoDS
from api.transformers.hpo_disease_pheno_ds import HPODiseasePhenoDS
from api.transformers.mgi_gene_pheno_ds import MGIGenePhenoDS
from api.transformers.mgi_gene_pheno_senay_ds import MgiGenePhenoSenayDS
from api.transformers.hpogold_disease_pheno_ds import HpoGoldDiseasePhenoDS
from api.transformers.hpo_gene_pheno import HPOGenePhenoDS

from django.conf import settings
from api.rdf.rdf_source import RDFSource


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Started transforming data to rdf'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--sources', type=str, help='specify list of sources to be transformed', ) 
        pass
                
    def handle(self, *args, **options):
        logger.info("Starting transforming source files to rdf")
        sources = options['sources']
        
        os.chdir(settings.TARGET_DATA_DIR)
        data_archive_dir =  'data-' + str(datetime.date.today())
        os.makedirs(data_archive_dir, exist_ok=True)
        data_archive_path = settings.TARGET_DATA_DIR + '/' + data_archive_dir

        sources_map = {
            'doid_dp': DOIDDiseasePhenoDS(data_archive_path), 
            'hpo_dp': HPODiseasePhenoDS(data_archive_path),
            'hpo_gp': HPOGenePhenoDS(data_archive_path),
            'mondo_dp': MondoDiseasePhenoDS(data_archive_path), 
            'patho_dp': PathoDiseasePhenoDS(data_archive_path),
            'hpogold_dp': HpoGoldDiseasePhenoDS(data_archive_path),
            'pubchem_dp': DrugPhenoDS(data_archive_path), 
            'txtmind_gp': TextminedhenoGenePhenoDS(data_archive_path), 
            'deep_gp': DeepphenoGenePhenoDS(data_archive_path),
            'mgi_gp': MGIGenePhenoDS(data_archive_path),
            'mgi_senay_gp': MgiGenePhenoSenayDS(data_archive_path),
            'patho_pp': PathogenPhenoDS(data_archive_path),
            'mp': MetabolitePhenoDS(data_archive_path)
        }   

        if not sources or (sources.strip() and not sources_map[sources.split(',')[0]]):
            logger.info("Transforming all datasets")
            for key in sources_map:
                self.transform(sources_map[key])
        else:
            for source in sources.split(","):
                logger.info("Transforming %s", source)
                self.transform(sources_map[source])

    def transform(self, source: RDFSource):
        logger.info("Started transformation %s", source.get_name())
        start_index = time.perf_counter()
        source.fetch()
        source.map()
        source.write()
        logger.info("Transformation time: %d sec", time.perf_counter() - start_index)
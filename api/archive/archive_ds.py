from django.conf import settings

from os import listdir
from os.path import isfile, join, splitext
from pathlib import Path

from api.rdfox import MimeType

import api.rdfox as rdfox

import signal
import logging
import datetime


logger = logging.getLogger(__name__)

RDF_DATA_ARCHIVE_FOLDER = getattr(settings, 'RDF_DATA_ARCHIVE_FOLDER', None)

class FileInfo:
 
   def __init__(self):
       self.full_name = None
       self.last_mod_time = 0
       self.extn = None
 
   def __str__(self):
       return 'Full Name: ' + self.full_name + '\n' + 'Extn: ' + self.extn + '\n' \
            + 'Last Modified Time: ' + strftime("%d %b %Y", time.gmtime(self.last_mod_time)) + '\n' \

#Define method to extract attributes from full file name
def populate_file_object(file):
   file_obj = FileInfo()
   file_obj.full_name = file
   file_extn = file.split('.')[len(file.split('.')) - 1]
   file_obj.extn = file_extn
   mod_time = os.path.getmtime(file)
   file_obj.last_mod_time = mod_time

   return file_obj

def find_latest_file():
    os.chdir(RDF_DATA_ARCHIVE_FOLDER)
   
    latest_file_obj = None 
    index = 0
    for file in os.listdir():
       if os.path.isfile(file):
            file_obj = populate_file_object(file)
            if index == 0:
               latest_file_obj = file_obj
            elif file_obj.last_mod_time > latest_file_obj.last_mod_time:
                latest_file_obj = file_obj
            index += 1

    return latest_file_obj


def archive():
    if RDF_DATA_ARCHIVE_FOLDER is None or not RDF_DATA_ARCHIVE_FOLDER:
        raise Exception("datasets configuration property 'archive.dir' is required")

    now = datetime.datetime.now()
    time_str = now.strftime('%Y-%m-%dT%H:%M')
    try:
        with open(RDF_DATA_ARCHIVE_FOLDER + '/phenotype_ds_bk-' + time_str + '.nt', 'w') as file:  
            file.write(rdfox.listAllTriples(MimeType.NTRIPLE.value))
                
    except Exception as e:
        logger.exception("message")

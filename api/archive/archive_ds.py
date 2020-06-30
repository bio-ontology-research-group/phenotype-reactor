from django.conf import settings

from os import listdir
from os.path import isfile, join, splitext
from pathlib import Path

import signal
import logging
import datetime
import time
import os
import tarfile
import operator

logger = logging.getLogger(__name__)

RDF_DATA_ARCHIVE_DIR = getattr(settings, 'TARGET_DATA_DIR', None)

class FileInfo:
 
    def __init__(self):
       self.full_name = None
       self.last_mod_time = 0
       self.extn = None
 
    def __str__(self):
       return 'Full Name: ' + self.full_name + '\n' \
            + 'Last Modified Time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.last_mod_time)) + '\n' \

    def to_dict(self):
      return {"full_name": self.full_name, "last_mod_time": time.strftime("%Y-%m-%d", time.gmtime(self.last_mod_time)), "extn": self.extn}

#Define method to extract attributes from full file name
def populate_dir_object(file):
   file_obj = FileInfo()
   file_obj.full_name = file
   mod_time = os.path.getmtime(file)
   file_obj.last_mod_time = mod_time
   return file_obj


def populate_file_object(file):
   file_obj = FileInfo()
   file_obj.full_name = file
   file_extn = file.split('.')[len(file.split('.')) - 1]
   file_obj.extn = file_extn
   mod_time = os.path.getmtime(file)
   file_obj.last_mod_time = mod_time
   return file_obj


def find_latest_file(isfile = True):
    os.chdir(RDF_DATA_ARCHIVE_DIR)
   
    latest_file_obj = None 
    index = 0
    for file in os.listdir():
        file_obj = None
        if isfile and os.path.isfile(file):
            file_obj = populate_file_object(file)
            if not latest_file_obj:
                latest_file_obj = file_obj
            elif file_obj.last_mod_time > latest_file_obj.last_mod_time:
                latest_file_obj = file_obj

        elif not isfile and os.path.isdir(file):
            file_obj = populate_dir_object(file)
            if not latest_file_obj:
                latest_file_obj = file_obj
            elif file_obj.last_mod_time > latest_file_obj.last_mod_time:
                latest_file_obj = file_obj
        
        index += 1

    return latest_file_obj

def find():
    os.chdir(RDF_DATA_ARCHIVE_DIR)
   
    arhived_files = []
    for file in os.listdir():
        file_obj = None
        if os.path.isfile(file) and '.gz' in splitext(file)[1]:
            arhived_files.append(populate_file_object(file))
    arhived_files.sort(key=lambda x: x.last_mod_time, reverse=True)
    return [item.to_dict() for item in arhived_files]


def archive():
    if RDF_DATA_ARCHIVE_DIR is None or not RDF_DATA_ARCHIVE_DIR:
        raise Exception("configuration property 'target.dir' is required")

    dataset_dir = find_latest_file(False)
    if not dataset_dir:
        raise Exception("there is no dataset to archive")

    try:
        filename = dataset_dir.full_name + ".tar.gz"
        logger.info("archiving rdf data {filename}".format(filename= filename))
        with tarfile.open(filename, "w:gz") as tar:
            tar.add(dataset_dir.full_name, arcname=os.path.basename(dataset_dir.full_name))
                
    except Exception as e:
        logger.exception("message")

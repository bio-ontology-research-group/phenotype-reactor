from django.conf import settings
from enum import Enum

import requests
import logging


logger = logging.getLogger(__name__)

RDF_STORE_URL = getattr(settings, 'RDF_STORE_URL')
RDF_STORE_DS = getattr(settings, 'RDF_STORE_DS')
RDF_STORE_USER = getattr(settings, 'RDF_STORE_USER')
RDF_STORE_PWD = getattr(settings, 'RDF_STORE_PWD')

DS_URL = RDF_STORE_URL + '/datastores/' + RDF_STORE_DS
CONTENT_URL = DS_URL + '/content'
SPARQL_URL = DS_URL+ '/sparql'

class MimeType(Enum):
    TRUTLE = "text/turtle"
    NTRIPLE = "application/n-triples"
    NQUADS = "application/n-quads"
    OWLFUNC = "text/owl-functional"
    TRIG = "application/trig"

def upload(content, format='turtle'):
    response = None
    if format is 'turtle':
        response = requests.post(CONTENT_URL, data=content)

    if response.status_code == requests.codes.ok:
        return
    elif response.status_code in [requests.codes.no_content,  requests.codes.not_found]:
        raise Exception('Failed to add content to datastore')


def executeSelect(query, format=None):
    response = requests.get(SPARQL_URL, params={"query": query}) 
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise Exception('Failed to run select query')

def listAllTriples(format=MimeType.TRUTLE.value):
    response = requests.get(CONTENT_URL, headers={"Accept": format})
    if response.status_code == requests.codes.ok:
        return response.text
    else :
        raise Exception('Failed to obtain triples from datastore')

def clean():
    response = requests.delete(CONTENT_URL)
    if response.status_code == requests.codes.no_content:
        return response.text
    else :
        raise Exception('Failed to delete content from datastore')
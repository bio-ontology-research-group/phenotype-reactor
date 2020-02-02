from django.conf import settings

import requests
import logging

logger = logging.getLogger(__name__)

RDF_STORE_URL = getattr(settings, 'RDF_STORE_URL')
RDF_STORE_DS = getattr(settings, 'RDF_STORE_DS')
RDF_STORE_USER = getattr(settings, 'RDF_STORE_USER')
RDF_STORE_PWD = getattr(settings, 'RDF_STORE_PWD')

API_URL = RDF_STORE_URL + '/' + RDF_STORE_DS
CONTENT_URL = RDF_STORE_URL + '/' + RDF_STORE_DS + '/content'
SPARQL_URL = RDF_STORE_URL + '/' + RDF_STORE_DS + '/sparql'

def upload(content, format='turtle'):
    response = None
    if format is 'turtle':
        response = requests.post(CONTENT_URL, data=content)

    if response.status_code == requests.codes.ok:
        return
    else:
        response.status_code == requests.codes.no_content:
        raise Exception('Failed to add content to datastore')


def executeSelect(query, format=None):
    response = requests.get(SPARQL_URL, params={"query": query}) 
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.status_code == requests.codes.no_content:
        raise Exception('Failed to run select query')

def listAllTriples():
    response = requests.get(CONTENT_URL, headers={"Accept": "text/turtle"})
    if response.status_code == requests.codes.ok:
        return response.text
    else:
        response.status_code == requests.codes.no_content:
        raise Exception('Failed to obtain triples from datastore')
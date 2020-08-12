import logging

from elasticsearch import Elasticsearch
from django.conf import settings

logger = logging.getLogger(__name__)

esUrl = settings.ABEROWL_ES_URL.split(",")

def connection():
    if settings.ABEROWL_ES_USERNAME and settings.ABEROWL_ES_PASSWORD:
        es = Elasticsearch(esUrl, http_auth=(settings.ABEROWL_ES_USERNAME, settings.ABEROWL_ES_PASSWORD))
    else :
        es = Elasticsearch(esUrl)
    return es

# executes query on given index
def execute(indexname, query):
    try:
        es = connection()
        res = es.search(index=indexname, body=query, request_timeout=(10 * 60))
        return res
    except Exception as e:
        logger.exception("message")

# find owl classes indexed in aberowl repository
def find_classes(ontology):
    try:
        es = connection()
        query = {
            "size" : 2500000,
            "query": { 
                "bool": { 
                    "filter": [{ 
                        "term": { 
                        "ontology": ontology 
                        } 
                    }] 
                } 
            }
        }
        result = es.search(index=settings.ABEROWL_ES_IDX_CLASS, body=query, request_timeout=(10 * 60), scroll='3m')
        return list(map(lambda hit: hit['_source'], result['hits']['hits']))
    except Exception as e:
        logger.exception("message")

# gets ontology details in aberowl repository
def get_ontology(ontology):
    query = {
        "query": { 
            "term" : { "ontology" :  ontology }
        }
    }

    result = execute(settings.ABEROWL_ES_IDX_ONTOLOGY, query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
        
import logging

from elasticsearch import Elasticsearch
from django.conf import settings

logger = logging.getLogger(__name__)

es = None
esUrl = settings.LOOKUP_ES_URL
if settings.LOOKUP_ES_USERNAME and settings.LOOKUP_ES_PASSWORD:
    es = Elasticsearch(esUrl, http_auth=(settings.LOOKUP_ES_USERNAME, settings.LOOKUP_ES_PASSWORD), timeout=30)
else :
    es = Elasticsearch(esUrl, timeout=30)

VALUESET_INDEX_NAME = "biomed_valueset"
ENTITY_INDEX_NAME = "biomed_entity"
DEFAULT_PAGE_SIZE = 10

VALUESET_INDEX_SETTINGS = {
  "mappings" : {
    "properties" : {
      "description" : {
        "type" : "text"
      },
      "name" : {
        "type" : "keyword",
        "normalizer" : "vs_normalizer"
      },
      "valueset" : {
        "type" : "keyword",
        "normalizer" : "vs_normalizer"
      }
    }
  },
  "settings" : {
    "analysis" : {
      "normalizer" : {
        "vs_normalizer" : {
          "filter" : [
            "lowercase"
          ],
          "type" : "custom"
        }
      }
    }
  }
}


ENTITY_INDEX_SETTINGS = {
  "mappings" : {
    "properties" : {
      "entity" : {
        "type" : "keyword"
      },
      "definition" : {
        "type" : "text"
      },
      "identifier" : {
        "type" : "keyword"
      },
      "label" : {
        "type" : "keyword",
        "normalizer" : "entity_normalizer"
      },
      "valueset" : {
        "type" : "keyword",
        "normalizer" : "entity_normalizer"
      },
      "entity_type" : {
        "type" : "keyword",
        "normalizer" : "entity_normalizer"
      },
      "synonym" : {
        "type" : "text"
      }
    }
  },
  "settings" : {
    "analysis" : {
      "normalizer" : {
        "entity_normalizer" : {
          "filter" : [
            "lowercase"
          ],
          "type" : "custom"
        }
      }
    }
  }
}

def create(index, index_settings):
  try:
    es.indices.create(index=index, body=index_settings, ignore=400)
  except Exception as e:
      logger.exception("message")

def index(index, document):
  try:
    result = es.index(index=index, body=document)
    if result["result"] == "created":
      return True
    return False 
  except Exception as e:
    logger.exception("message")

def delete_valueset(valueset_name):
  try:
    query = {
        "query": {
          "match": {
            "valueset": valueset_name
          } 
        }
      } 
    result = es.delete_by_query(index=VALUESET_INDEX_NAME, body=query)
    result = es.delete_by_query(index=ENTITY_INDEX_NAME, body=query)
  except Exception as e:
    logger.exception("message")

def find_by_startswith(term, entity_type):
  try:
    query = {
        "size" : DEFAULT_PAGE_SIZE,
        "query": { 
          "bool": { 
            "must": [
              { "prefix": { "label": { "value": term } }}, 
              { "term": { "entity_type": entity_type } }
            ] 
          } 
        }
      }
    result = es.search(index=settings.ABEROWL_ES_IDX_CLASS, body=query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
  except Exception as e:
      logger.exception("message")

def find_by_iris(iris):
  try:
    filter_part = []
    for iri in iris:
      filter_part.append({ "term": { "entity": { "value": iri } } })


    query = {
        "size" : 1000,
        "query": { 
          "bool": { 
            "must": filter_part
          } 
        }
      }
    result = es.search(index=settings.ABEROWL_ES_IDX_CLASS, body=query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
  except Exception as e:
      logger.exception("message")

  

logger.info("Creating index '%s' if not exists", VALUESET_INDEX_NAME)
create(VALUESET_INDEX_NAME, VALUESET_INDEX_SETTINGS)

logger.info("Creating index '%s' if not exists", ENTITY_INDEX_NAME)
create(ENTITY_INDEX_NAME, ENTITY_INDEX_SETTINGS)






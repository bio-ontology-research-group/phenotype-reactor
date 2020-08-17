import logging
import uuid

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from django.conf import settings

logger = logging.getLogger(__name__)

es = None
esUrl = settings.LOOKUP_ES_URL.split(",")
if settings.LOOKUP_ES_USERNAME and settings.LOOKUP_ES_PASSWORD:
    es = Elasticsearch(esUrl, http_auth=(settings.LOOKUP_ES_USERNAME, settings.LOOKUP_ES_PASSWORD))
else :
    es = Elasticsearch(esUrl)

VALUESET_INDEX_NAME = settings.LOOKUP_ES_VALUESET_INDEX_NAME
ENTITY_INDEX_NAME = settings.LOOKUP_ES_ENTITY_INDEX_NAME
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

def index_by_bulk(data):
  try:
    entries = []
    for entry in data:
      entries.append({ 
          "_index": ENTITY_INDEX_NAME,
          "_id": uuid.uuid4().hex,
          "_source": entry
      })
    result = helpers.bulk(es, entries, refresh=True, request_timeout=(60 * 10))
    logger.info("entries effected: %d", result[0])
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
    result = es.delete_by_query(index=ENTITY_INDEX_NAME, body=query, request_timeout=(60 * 30))
  except Exception as e:
    logger.exception("message")

def find_entity_by_startswith(term, valueset):
  try:
    criteria = None
    if valueset.strip():
      criteria = [
              { "prefix": { "label": { "value": term } }}, 
              { "term": { "valueset": valueset } }
            ] 
    else:
      criteria = [ { "prefix": { "label": { "value": term }}} ] 
    query = {
        "size" : DEFAULT_PAGE_SIZE,
        "query": { 
          "bool": { 
            "must": criteria
          } 
        }
      }
    result = es.search(index=ENTITY_INDEX_NAME, body=query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
  except Exception as e:
      logger.exception("message")

def find_entity_by_iris(iris, valueset):
  try:
    filter_part = []
    if valueset:
      print(valueset)
      filter_part.append({ "term": { "valueset" : valueset }})
    filter_part.append({ "terms": { "entity": iris } })
    query = {
        "size" : 10000,
        "query": { 
          "bool": { 
            "filter": filter_part
          } 
        }
      }
    result = es.search(index=ENTITY_INDEX_NAME, body=query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
  except Exception as e:
      logger.exception("message")

def find_all_valueset():
  try:
    query = {
        "size": 100,
        "query": { 
          "match_all": { } 
        }
      }
    result = es.search(index=VALUESET_INDEX_NAME, body=query)
    return list(map(lambda hit: hit['_source'], result['hits']['hits']))
  except Exception as e:
      logger.exception("message")

  

logger.info("Creating index '%s' if not exists", VALUESET_INDEX_NAME)
create(VALUESET_INDEX_NAME, VALUESET_INDEX_SETTINGS)

logger.info("Creating index '%s' if not exists", ENTITY_INDEX_NAME)
create(ENTITY_INDEX_NAME, ENTITY_INDEX_SETTINGS)






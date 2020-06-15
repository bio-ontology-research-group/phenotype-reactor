
import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

BIO2VEC_MOSTSIM_API_URL = settings.BIO2VEC_API_URL + '/api/bio2vec/mostsimilar'

def find_most_similar(iri):
    url = f'{BIO2VEC_MOSTSIM_API_URL}?id={iri}&dataset={settings.BIO2VEC_DATASET}'
    response = requests.get(url)
    result = response.json()
    if result['result']:
        similar = result['result'][iri]
        similar_iris = []
        for item in similar:
            similar_iris.append(item['_source']['id'])
        return similar_iris
    return []
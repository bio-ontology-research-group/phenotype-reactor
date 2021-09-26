
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib import parse
from urllib.parse import urlencode

import logging
import requests

logger = logging.getLogger(__name__)

ABEROWL_ENDPOINT = 'http://aber-owl.net/api/sparql'

def execute_sparql(query, format):
    param = {'query': query, 'format':format}
    querystr = urlencode(param, doseq=True)
    query_url=f"{ABEROWL_ENDPOINT}?{querystr}"
    response = requests.get(query_url)
    return response
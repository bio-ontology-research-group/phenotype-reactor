
from django.conf import settings
from django.http import HttpResponseRedirect

VIRTUOSO_HOST = getattr(settings, 'VIRTUOSO_HOST')
VIRTUOSO_SPARQL_PORT = getattr(settings, 'VIRTUOSO_SPARQL_PORT')
SPARQL_ENDPOINT_URL = VIRTUOSO_HOST + ":" +VIRTUOSO_SPARQL_PORT

def execute_sparql(query, format):
    query_url="{endpoint}?query={query}&format={format}&timeout=0&debug=on&run={run}" \
                .format(
                    endpoint=SPARQL_ENDPOINT_URL, 
                    query=parse.quote(query), 
                    format=parse.quote(format), 
                    run=parse.quote('Run Query'))
    logger.debug("redirect to:" + query_url)
    response = HttpResponseRedirect(redirect_to=query_url)
    return response
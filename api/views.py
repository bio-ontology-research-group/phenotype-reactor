import logging
import json
import os

import api.archive.archive_ds as archive
import api.lookup.lookup_elasticsearch as lookup_es  

from django.http import Http404, HttpResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.association import Association
from api.bio2vec_api import find_most_similar


logger = logging.getLogger(__name__) 

class FindAssociation(APIView):
    """
    List associations by given criteria
    """

    service = Association()

    def get(self, request, format=None):
        try:
            concept = request.GET.get('concept', None)
            phenotype = request.GET.get('phenotype', None)
            concept_type = request.GET.get('type', None)

            (response, query) = self.service.find(concept, phenotype) 
            result = response.json()
            result['query'] = query
            return Response(result)
        except Exception as e:
            logger.exception("message")

class FindMostSimilar(APIView):
    """
    List associations by given criteria
    """

    service = Association()
    def get(self, request, format=None):
        try:
            concept = request.GET.get('concept', None)
            type_iri = request.GET.get('type', None)
            (response, query) = self.service.find_similar_concepts(concept, type_iri) 
            result = response.json()
            result['query'] = query
            return Response(result)
        except Exception as e:
            logger.exception("message")

class GetLatestDataArchived(APIView):
    """
    Get latest
    """
    def get(self, request, format=None):
        try:
            file = archive.find_latest_file()
            file_path = os.path.join(settings.TARGET_DATA_DIR, file.full_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/tar+gzip")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response
            raise Http404
        except Exception as e:
            logger.exception("message")

class FindDataArchived(APIView):
    """
    Get latest
    """
    def get(self, request, format=None):
        try:
            result = archive.find()
            return Response(result)
        except Exception as e:
            logger.exception("message")

class FindEntityByLabelStartsWith(APIView):
    """
    List associations by given criteria
    """

    def get(self, request, format=None):
        try:
            term = request.GET.get('term', None)
            valueset = request.GET.get('valueset', None)

            result = lookup_es.find_entity_by_startswith(term, valueset) 
            return Response(result)
        except Exception as e:
            logger.exception("message")
            

class FindEntityByIris(APIView):
    """
    List associations by given criteria
    """

    def post(self, request, format=None):
        try:
            entity_iris = request.data['iri']

            valueset = None
            if 'valueset' in request.data:
                valueset = request.data['valueset']

            if not entity_iris:
                raise RuntimeException("'iri' property is required")

            result = lookup_es.find_entity_by_iris(entity_iris, valueset) 
            return Response(result)
        except Exception as e:
            logger.exception("message")

class FindValueset(APIView):
    """
    List associations by given criteria
    """

    def get(self, request, format=None):
        try:
            result = lookup_es.find_all_valueset()
            return Response(result)
        except Exception as e:
            logger.exception("message")
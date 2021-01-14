import logging
import json
import os
import requests

import api.archive.archive_ds as archive
import api.lookup.lookup_elasticsearch as lookup_es  

from django.http import Http404, HttpResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.associations import Associations
from api.associationsets import Associationsets
from api.bio2vec_api import find_most_similar


logger = logging.getLogger(__name__) 

class FindAssociation(APIView):
    """
    List associations by given criteria
    """

    service = Associations()

    def get(self, request, format=None):
        try:
            concept = request.GET.get('concept', None)
            phenotype = request.GET.get('phenotype', None)
            concept_type = request.GET.get('type', None)
            evidences = request.GET.getlist('evidence')
            associationsets = request.GET.getlist('associationset')
            limit = request.GET.get('limit', None)
            offset = request.GET.get('offset', None)
            order_by = request.GET.get('orderBy', None)

            (response, query) = self.service.find(concept, phenotype, concept_type, evidences, associationsets, limit, offset, order_by) 
            
            if response.status_code == requests.codes.ok:
                result = response.json()
                result['query'] = query
                return Response(result)
            
            if response.status_code == requests.codes.bad_request:
                raise Exception(response.text)
        except Exception as e:
            logger.exception("message")

class FindMostSimilar(APIView):
    """
    List associations by given criteria
    """

    service = Associations()
    def get(self, request, format=None):
        try:
            concept = request.GET.get('concept', None)
            type_iri = request.GET.get('type', None)
            order_by = request.GET.get('orderBy', None)
            limit = request.GET.get('limit', None)
            if limit:
                (response, query) = self.service.find_similar_concepts(concept, type_iri, order_by, limit) 
            else :
                (response, query) = self.service.find_similar_concepts(concept, type_iri, order_by) 
            if response.status_code == requests.codes.ok:
                result = response.json()
                result['query'] = query
                return Response(result)
            
            if response.status_code == requests.codes.bad_request:
                raise Exception(response.text)
        except Exception as e:
            logger.exception("message")

class FindMatchingPhenotypes(APIView):
    """
    List of matching phenotypes between two biomedical concepts
    """

    service = Associations()

    def get(self, request, format=None):
        try:
            source = request.GET.get('source', None)
            target = request.GET.get('target', None)

            (response, query) = self.service.find_matching_phenotypes(source, target)
            
            if response.status_code == requests.codes.ok:
                result = response.json()
                result['query'] = query
                return Response(result)
            
            if response.status_code == requests.codes.bad_request:
                raise Exception(response.text)
        except Exception as e:
            logger.exception("message")

class FindMatchingPhenotypesSuperclasses(APIView):
    """
    List of matching phenotype super classes between two biomedical concepts
    """

    service = Associations()

    def get(self, request, format=None):
        try:
            source = request.GET.get('source', None)
            target = request.GET.get('target', None)

            result = self.service.find_matching_phenotype_superclasses(source, target)
            return Response(result)
        except Exception as e:
            logger.exception("message")

class FindAssociationset(APIView):
    """
    List associationsets
    """

    service = Associationsets()
    def get(self, request, format=None):
        try:
            (response, query) = self.service.find_associationsets()
            if response.status_code == requests.codes.ok:
                return Response(response.json())
            
            if response.status_code == requests.codes.bad_request:
                raise Exception(response.text)
        except Exception as e:
            logger.exception("message")
        except Exception as e:
            logger.exception("message")



class GetAssociationsetByIdentifier(APIView):
    """
    Get associationset by identifier
    """

    service = Associationsets()
    def get(self, request, identifier, format=None):
        try:
            (response, query) = self.service.find_associationset_by_identifier(identifier)
            if response.status_code == requests.codes.ok:
                return Response(response.json())
            
            if response.status_code == requests.codes.bad_request:
                raise Exception(response.text)
        except Exception as e:
            logger.exception("message")
        except Exception as e:
            logger.exception("message")


class GetAssociationsetConfig(APIView):
    """
    Get Associationsets configuration
    """

    def get(self, request, format=None):
        return Response(settings.ASSOCIATION_SET_CONFIG)

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
            valueset = request.GET.getlist('valueset')
            pagesize = request.GET.get('pagesize', None)
            result = lookup_es.find_entity_by_startswith(term, valueset, pagesize) 
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


class FindGeneBySymbols(APIView):
    """
    List associations by given criteria
    """

    def post(self, request, format=None):
        try:
            symbols = request.data['symbols']

            valueset = None
            if 'valueset' in request.data:
                valueset = request.data['valueset']
            
            organism_type = None
            if 'organism_type' in request.data:
                organism_type = request.data['organism_type']

            if not symbols:
                raise RuntimeException("'symbols' property is required")

            result = lookup_es.find_gene_by_symbols(symbols, valueset, organism_type) 
            return Response(result)
        except Exception as e:
            logger.exception("message")
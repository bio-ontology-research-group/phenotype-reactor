from django.http import Http404, HttpResponse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import api.archive.archive_ds as archive
from api.association import Association

import logging
import os

logger = logging.getLogger(__name__) 

class AssociationList(APIView):
    service = Association()

    """
    List associations by given criteria
    """
    def get(self, request, format=None):
        return self.service.findConceptAssociation(None) 
        

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
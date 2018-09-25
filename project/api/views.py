from ast import literal_eval as make_tuple
from django.contrib.gis.geos import Polygon
from rest_framework import viewsets, permissions

from .models import Nation, Territory, DiplomaticRelation
from .serializers import NationSerializer, TerritorySerializer, DiplomaticRelationSerializer
from .filters import TerritoryFilter

class NationViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Nation model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Nation.objects.all()
    serializer_class = NationSerializer
    lookup_field = 'url_id'

    # TODO use request.user to update revision table

class TerritoryViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Territory model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TerritorySerializer
    filter_class = TerritoryFilter

    queryset = Territory.objects.all()

    # TODO use request.user to update revision table

class DiplomaticRelationViewSet(viewsets.ModelViewSet):
    """
    Viewset for the DiplomaticRelation model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = DiplomaticRelation.objects.all()
    serializer_class = DiplomaticRelationSerializer

    # TODO use request.user to update revision table

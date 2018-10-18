from rest_framework import viewsets, permissions

from .models import PoliticalEntity, Territory, DiplomaticRelation
from .serializers import (
    PoliticalEntitySerializer,
    TerritorySerializer,
    DiplomaticRelationSerializer,
)
from .filters import TerritoryFilter


class PoliticalEntityViewSet(viewsets.ModelViewSet):
    """
    Viewset for the PoliticalEntity model
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PoliticalEntity.objects.all()
    serializer_class = PoliticalEntitySerializer
    lookup_field = "url_id"

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

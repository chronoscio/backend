from ast import literal_eval as make_tuple
from django.contrib.gis.geos import Polygon
from rest_framework import viewsets, permissions

from .models import PoliticalEntity, Territory, DiplomaticRelation
from .serializers import PoliticalEntitySerializer, TerritorySerializer, DiplomaticRelationSerializer

class PoliticalEntityViewSet(viewsets.ModelViewSet):
    """
    Viewset for the PoliticalEntity model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PoliticalEntity.objects.all()
    serializer_class = PoliticalEntitySerializer
    lookup_field = 'url_id'

    # TODO use request.user to update revision table

class TerritoryViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Territory model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TerritorySerializer

    queryset = Territory.objects.all()

    def get_queryset(self):
        bounds = self.request.query_params.get('bounds', None)
        if bounds is not None:
            geom = Polygon(make_tuple(bounds), srid=4326)
            self.queryset = Territory.objects.filter(geo__intersects=geom)

        date = self.request.query_params.get('date', None)
        if date is not None:
            self.queryset = Territory.objects.filter(start_date__lte=date,
                                                     end_date__gte=date)

        return self.queryset

    # TODO use request.user to update revision table

class DiplomaticRelationViewSet(viewsets.ModelViewSet):
    """
    Viewset for the DiplomaticRelation model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = DiplomaticRelation.objects.all()
    serializer_class = DiplomaticRelationSerializer

    # TODO use request.user to update revision table

from ast import literal_eval as make_tuple
from django.contrib.gis.geos import Polygon
from rest_framework import viewsets, permissions

from .models import Nation, Territory
from .serializers import NationSerializer, TerritorySerializer

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

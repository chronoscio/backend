from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from .models import Nation, Territory
from .serializers import NationSerializer, TerritorySerializer, UserSerializer
from .permissions import IsStaffOrSpecificUser

class NationViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Nation model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Nation.objects.all()
    serializer_class = NationSerializer
    lookup_field = "url_id"

    # TODO use request.user to update revision table

class TerritoryViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Territory model
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Territory.objects.all()
    serializer_class = TerritorySerializer

    # TODO use request.user to update revision table

class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for the User model
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return (permissions.AllowAny() if self.request.method == 'POST'
                else IsStaffOrSpecificUser()),

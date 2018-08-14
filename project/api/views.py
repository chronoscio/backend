from django.contrib.auth.models import User
from rest_framework import viewsets, permissions

from .models import Nation, Territory
from .serializers import NationSerializer, TerritorySerializer, UserSerializer
from .permissions import IsStaffOrSpecificUser, get_token_auth_header, requires_scope

# TODO delet this
from django.http import JsonResponse
from rest_framework.decorators import api_view


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

def public(request):
    return JsonResponse({'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'})


@api_view(['GET'])
def private(request):
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated to see this.'})


@api_view(['GET'])
@requires_scope('user:staff')
def private_scoped(request):
    return JsonResponse({'message': 'Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.'})

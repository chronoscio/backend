from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.http import HttpResponseRedirect
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


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_staff = True
            new_user.save()
            try:
                new_user.groups.add(Group.objects.get(name='mapper'))
            except Group.DoesNotExist:
                pass

            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            login(request, user)
            return HttpResponseRedirect("/admin")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})

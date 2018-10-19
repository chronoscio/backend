from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

ROUTER = DefaultRouter()
ROUTER.register(r"politicalentities", views.PoliticalEntityViewSet)
ROUTER.register(r"territories", views.TerritoryViewSet)
ROUTER.register(r"diprels", views.DiplomaticRelationViewSet)

urlpatterns = [path("", include(ROUTER.urls))]

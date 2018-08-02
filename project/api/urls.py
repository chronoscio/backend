from django.urls import path, include
from rest_framework.router import DefaultRouter

from . import views

ROUTER = DefaultRouter()
ROUTER.register(r'nations', views.NationViewSet)
ROUTER.register(r'territories', views.TerritoryViewSet)

urlpatterns = [
    path('', include(ROUTER.urls))
]

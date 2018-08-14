from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

ROUTER = DefaultRouter()
ROUTER.register(r'nations', views.NationViewSet)
ROUTER.register(r'territories', views.TerritoryViewSet)
ROUTER.register(r'accounts', views.UserViewSet)

urlpatterns = [
    path('', include(ROUTER.urls)),
    #TODO delet
    path('public', views.public),
    path('private', views.private),
    path('private-scoped', views.private_scoped),
]

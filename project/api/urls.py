from django.urls import path
from graphene_django.views import GraphQLView

from . import views

urlpatterns = [
    path('', GraphQLView.as_view(graphiql=True), name='graphql'),
]

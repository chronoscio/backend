from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
import graphene

from django.contrib.gis.db.models.fields import GeometryField

from .models import Territory as TerritoryModel
from .models import Nation as NationModel

@convert_django_field.register(GeometryField)
def convert_geo_field_to_string(field, registry=None):
    return graphene.String()

class Territory(DjangoObjectType):
    class Meta:
        model = TerritoryModel

class Query(graphene.ObjectType):
    territories = graphene.List(Territory)

    def resolve_territories(self, info):
        return TerritoryModel.objects.all()

schema = graphene.Schema(query=Query)

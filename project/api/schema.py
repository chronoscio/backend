import graphene

from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field

from django.core.exceptions import ValidationError
from django.contrib.gis.db.models.fields import GeometryField

from .models import Territory as TerritoryModel
from .models import Nation as NationModel
from .helpers import *

@convert_django_field.register(GeometryField)
def convert_geo_field_to_string(field, registry=None):
    """Conversion for the geodjango Geometry field"""

    return graphene.String()

class NationCreateInput(graphene.InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """

    name = graphene.String(required=True)
    local_name = graphene.String(required=False)
    wikipedia = graphene.String(required=False)

#Objects
class Nation(DjangoObjectType):
    """Corresponds to the Nation model in django"""

    class Meta:
        model = NationModel

class Territory(DjangoObjectType):
    """Corresponds to the Territory model in django"""

    class Meta:
        model = TerritoryModel

#Nation operations
class CreateNation(graphene.relay.ClientIDMutation):

    class Input:
        # NationCreateInput class used as argument here.
        nation = graphene.Argument(NationCreateInput)

    new_nation = graphene.Field(Nation)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **args):
    # def mutate_and_get_payload(cls, args, context, info):

        nation_data = args.get('nation') # get the nation input from the args
        nation = NationModel() # get an instance of the nation model here
        new_nation = update_create_instance(nation, nation_data) # use custom function to create nation

        return cls(new_nation=new_nation) # newly created nation instance returned.

class UpdateNation(graphene.relay.ClientIDMutation):

    class Input:
        nation = graphene.Argument(NationCreateInput) # get the nation input from the args
        id = graphene.String(required=True) # get the nation id

    errors = graphene.List(graphene.String)
    updated_nation = graphene.Field(Nation)

    @classmethod
    def mutate_and_get_payload(cls, args, context, info):

        try:
            nation_instance = get_object(NationModel, args['id']) # get nation by id
            if nation_instance:
                # modify and update nation model instance
                nation_data = args.get('nation')
                updated_nation = update_create_instance(nation_instance, nation_data)
                return cls(updated_nation=updated_nation)
        except ValidationError as e:
            # return an error if something wrong happens
            return cls(updated_nation=None, errors=get_errors(e))

#Query
class Query(graphene.ObjectType):
    """Retrieves data for GraphQL queries"""

    nations = graphene.List(Nation)
    territories = graphene.List(Territory)

    def resolve_territories(self):
        """Returns a list of all Territories"""

        return TerritoryModel.objects.all()

    def resolve_nations(self):
        """Returns a list of all Nations"""

        return NationModel.objects.all()

#Mutation
class Mutation(graphene.ObjectType):
    """Maniuplates data for GraphQL mutations"""

    create_nation = CreateNation.Field()
    update_nation = UpdateNation.Field()

SCHEMA = graphene.Schema(query=Query, mutation=Mutation)

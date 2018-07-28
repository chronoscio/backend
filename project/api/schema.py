import json
import graphene

from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField

from django.core.exceptions import ValidationError
from django.contrib.gis.db.models.fields import MultiPolygonField

from .models import Territory as TerritoryModel
from .models import Nation as NationModel
from .helpers import *

#Geometry Field Conversion
class GeoJSON(graphene.Scalar):

    @classmethod
    def serialize(cls, value):
        return json.loads(value.geojson)

@convert_django_field.register(MultiPolygonField)
def convert_geo_field_to_geojson(field, registry=None):
    """Conversion for the geodjango MultiPolygon field"""

    return graphene.Field(
        GeoJSON,
        description=field.help_text
    )

#Objects
class Nation(DjangoObjectType):
    """Corresponds to the Nation model in django"""

    class Meta:
        model = NationModel
        filter_fields = ['name']
        interfaces = (graphene.relay.Node, )

class Territory(DjangoObjectType):
    """Corresponds to the Territory model in django"""

    class Meta:
        model = TerritoryModel
        filter_fields = ['start_date', 'end_date', 'nation']
        interfaces = (graphene.relay.Node, )

#InputObjectTypes
class NationCreateInput(graphene.InputObjectType):
    """
    Class created to accept input data for the Nation object
    """

    name = graphene.String(required=True)
    color = graphene.String(required=True)
    aliases = graphene.String(required=False)
    description = graphene.String(required=False)
    wikipedia = graphene.String(required=False)


class TerritoryCreateInput(graphene.InputObjectType):
    """
    Class created to accept input data for the Territory object
    """

    start_date = graphene.types.datetime.Date(required=True)
    end_date = graphene.types.datetime.Date(required=True)
    geo = graphene.String(required=True)
    nation = graphene.ID(required=True)

#Nation operations
class CreateNation(graphene.relay.ClientIDMutation):

    class Input:
        # NationCreateInput class used as argument here.
        nation = NationCreateInput(required=True)

    new_nation = graphene.Field(Nation)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        new_nation = update_create_instance(NationModel(), input.get("nation"))
        #nation_data = args.get('nation') # get the nation input from the args
        #nation = NationModel() # get an instance of the nation model here
        #new_nation = update_create_instance(nation, nation_data) # use custom function to create nation

        return CreateNation(new_nation=new_nation) # newly created nation instance returned.

class UpdateNation(graphene.relay.ClientIDMutation):

    class Input:
        nation = graphene.Argument(NationCreateInput) # get the nation input from the args
        id = graphene.String(required=True) # get the nation id

    errors = graphene.List(graphene.String)
    updated_nation = graphene.Field(Nation)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **args):

        try:
            nation_instance = get_object(NationModel, args['id'])# get nation by id
            if nation_instance:
                # modify and update nation model instance
                nation_data = args.get('nation')
                updated_nation = update_create_instance(nation_instance, nation_data)
                return cls(updated_nation=updated_nation)
        except ValidationError as e:
            # return an error if something wrong happens
            return cls(updated_nation=None, errors=get_errors(e))

class CreateTerritory(graphene.relay.ClientIDMutation):

    class Input:
        # NationCreateInput class used as argument here.
        territory = graphene.Argument(TerritoryCreateInput)

    new_territory = graphene.Field(Territory)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **args):

        territory_data = args.get('territory') # get the territory input from the args
        territory = TerritoryModel() # get an instance of the territory model here
        new_territory = update_create_instance(territory,
                                               territory_data,
                                               exception=['id', 'nation']) # use custom function to create territory

        nation = NationModel.objects.get(pk=territory_data.nation)
        setattr(new_territory, 'nation', nation)
        new_territory.save()

        return cls(new_territory=new_territory) # newly created territory instance returned.

class UpdateTerritory(graphene.relay.ClientIDMutation):

    class Input:
        territory = graphene.Argument(TerritoryCreateInput) # get the territory input from the args
        id = graphene.String(required=True) # get the territory id

    errors = graphene.List(graphene.String)
    updated_territory = graphene.Field(Territory)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **args):

        try:
            territory_instance = get_object(TerritoryModel, args['id']) # get territory by id
            if territory_instance:
                # modify and update territory model instance
                territory_data = args.get('territory')
                updated_territory = update_create_instance(territory_instance, territory_data)
                return cls(updated_territory=updated_territory)
        except ValidationError as e:
            # return an error if something wrong happens
            return cls(updated_territory=None, errors=get_errors(e))

#Query
class Query(graphene.ObjectType):
    """Retrieves data for GraphQL queries"""

    all_territories = DjangoFilterConnectionField(Territory)
    all_nations = DjangoFilterConnectionField(Nation)

    territory = graphene.relay.Node.Field(Territory)
    nation = graphene.relay.Node.Field(Nation)

    ''''def resolve_all_territories(self, info):
        """Returns a list of all Territories"""

        return TerritoryModel.objects.all()

    def resolve_all_nations(self, info):
        """Returns a list of all Nations"""

        return NationModel.objects.all()

    def resolve_territory(self, info, **kwargs):
        """Returns a specific Territory"""

        id = kwargs.get('id')

        if id is not None:
            return TerritoryModel.objects.get(pk=id)

        return None

    def resolve_nation(self, info, **kwargs):
        """Returns a specific Nation"""

        id = kwargs.get('id')

        if id is not None:
            return NationModel.objects.get(pk=id)

        return None'''

#Mutation
class Mutation(graphene.AbstractType, graphene.ObjectType):
    """Maniuplates data for GraphQL mutations"""

    create_nation = CreateNation.Field()
    '''update_nation = UpdateNation.Field()

    create_territory = CreateTerritory.Field()
    update_territory = UpdateTerritory.Field()'''

schema = graphene.Schema(query=Query, mutation=Mutation)

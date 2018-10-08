"""
Factories let us easily generate test data:
https://github.com/FactoryBoy/factory_boy/
"""
import factory

from .models import Nation, Territory, DiplomaticRelation


class NationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nation

class TerritoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Territory

class DiplomaticRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DiplomaticRelation

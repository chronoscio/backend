"""
Factories let us easily generate test data:
https://github.com/FactoryBoy/factory_boy/
"""
import factory

from .models import PoliticalEntity, Territory, DiplomaticRelation


class PoliticalEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PoliticalEntity


class TerritoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Territory


class DiplomaticRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DiplomaticRelation

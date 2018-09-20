from json import loads, dumps

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.serializers import ModelSerializer

from .models import PoliticalEntity, Territory, DiplomaticRelation

class PoliticalEntitySerializer(ModelSerializer):
    """
    Serializes the PoliticalEntity model
    """
    class Meta:
        model = PoliticalEntity
        fields = '__all__'

class TerritorySerializer(ModelSerializer):
    """
    Serializes the Territory model as GeoJSON compatible data
    """
    def to_internal_value(self, data):
        ret = {}

        # Update ret to include passed in data
        for field, val in data.items():
            if field == 'PoliticalEntity':
                ret['PoliticalEntity'] = PoliticalEntity.objects.get(pk=val)
            if field != 'geo' and field != 'PoliticalEntity':
                ret[field] = val

        # Convert geo field to MultiPolygon if it is a FeatureCollection
        geojson = loads(data['geo'])
        if geojson['type'] == 'FeatureCollection':
            features = geojson['features']
            features_union = GEOSGeometry(dumps(features[0]['geometry']))
            features = features[1:]

            for feature in features:
                if feature['geometry']['type'] == 'Polygon':
                    features_union = features_union.union(GEOSGeometry(dumps(feature['geometry'])))

            ret['geo'] = features_union
        else:
            ret['geo'] = data['geo']

        return ret

    class Meta:
        model = Territory
        fields = '__all__'

class DiplomaticRelationSerializer(ModelSerializer):
    """
    Serializes the DiplomaticRelation model
    """
    class Meta:
        model = DiplomaticRelation
        fields = '__all__'

from json import loads, dumps

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.serializers import ModelSerializer

from .models import Nation, Territory

class NationSerializer(ModelSerializer):
    """
    Serializes the Nation model
    """
    class Meta:
        model = Nation
        fields = ("id",
                  "name",
                  "url_id",
                  "color",
                  "aliases",
                  "description",
                  "wikipedia",
                  "control_type")

class TerritorySerializer(ModelSerializer):
    """
    Serializes the Territory model as GeoJSON compatible data
    """
    def to_internal_value(self, data):
        ret = {}

        # Update ret to include passed in data
        for field, val in data.items():
            if field == 'nation':
                ret['nation'] = Nation.objects.get(pk=val)
            if field != 'geo' and field != 'nation':
                ret[field] = val

        # Convert geo field to MultiPolygon if it is a feature collection
        geojson = loads(data['geo'])
        if geojson['type'] == 'FeatureCollection':
            features = geojson['features']
            features_union = GEOSGeometry(dumps(features[0]['geometry']))
            features = features[1:]

            for feature in features:
                if feature['geometry']['type'] == 'Polygon':
                    features_union = features_union.union(GEOSGeometry(dumps(feature['geometry'])))

            ret['geo'] = features_union

        return ret

    class Meta:
        model = Territory
        fields = ("start_date",
                  "end_date",
                  "geo",
                  "nation")

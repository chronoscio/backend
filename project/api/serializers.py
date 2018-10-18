from json import loads, dumps

from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers
import geobuf
from .models import PoliticalEntity, Territory, DiplomaticRelation


class PoliticalEntitySerializer(serializers.ModelSerializer):
    """
    Serializes the PoliticalEntity model
    """

    class Meta:
        model = PoliticalEntity
        exclude = ("polymorphic_ctype",)


class GeoField(serializers.RelatedField):
    """
    Field Serializer for Territories
    """

    @classmethod
    def to_representation(self, value):
        # Compress geojson to geobuf and return as hexadecimal
        gbuf = geobuf.encode(loads(value.geojson))
        return gbuf.hex()


class TerritorySerializer(serializers.ModelSerializer):
    """
    Serializes the Territory model as GeoJSON compatible data
    """

    entity = serializers.SlugRelatedField(read_only=True, slug_field="url_id")

    geo = GeoField(read_only=True)

    def to_internal_value(self, data):
        ret = {}

        # Update ret to include passed in data
        for field, val in data.items():
            if field == "entity":
                ret["entity"] = PoliticalEntity.objects.get(pk=val)
            if field != "geo" and field != "entity":
                ret[field] = val

        # Convert geo field to MultiPolygon if it is a FeatureCollection
        geojson = loads(data["geo"])
        if geojson["type"] == "FeatureCollection":
            features = geojson["features"]
            features_union = GEOSGeometry(dumps(features[0]["geometry"]))
            features = features[1:]

            for feature in features:
                if feature["geometry"]["type"] == "Polygon":
                    features_union = features_union.union(
                        GEOSGeometry(dumps(feature["geometry"]))
                    )

            ret["geo"] = features_union
        else:
            ret["geo"] = data["geo"]

        return ret

    class Meta:
        model = Territory
        fields = "__all__"


class DiplomaticRelationSerializer(serializers.ModelSerializer):
    """
    Serializes the DiplomaticRelation model
    """

    entity = serializers.SlugRelatedField(read_only=True, slug_field="url_id")

    class Meta:
        model = DiplomaticRelation
        fields = "__all__"

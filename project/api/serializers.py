from django.contrib.auth.models import User
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
    class Meta:
        model = Territory
        fields = ("start_date",
                  "end_date",
                  "geo",
                  "nation")

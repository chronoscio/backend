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
                  "wikipedia")

class TerritorySerializer(ModelSerializer):
    """
    Serializes the Territory model as GeoJSON compatible data
    """
    class Meta:
        model = Territory
        fields = ("start_date",
                  "end_date",
                  "geo",
                  "nation",
                  "control_type")

class UserSerializer(ModelSerializer):
    """
    Serializes the User model, password cannot be read
    """
    class Meta:
        model = User
        fields = ("username", "email", "password")
        read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

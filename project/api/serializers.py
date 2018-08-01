from rest_framework import serializers
from .models import *

class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = ('id',
                  'name',
                  'color',
                  'aliases',
                  'description',
                  'wikipedia')

from rest_framework import serializers
from leomaster_app.models import Masterclass


class MasterclassSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(read_only=True, slug_field='name')
    master = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Masterclass
        fields = ('id',
                  'uid',
                  'title',
                  'description',
                  'date',
                  'duration',
                  'age_restriction',
                  'master',
                  'total_seats',
                  'avail_seats',
                  'price',
                  'online_price',
                  'location',
                  'max_complexity',
                  'complexity',
                  'creation_ts',
                  'modification_ts')

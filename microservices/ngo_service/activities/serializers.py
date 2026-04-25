from rest_framework import serializers
from .models import NGOActivity

class ActivitySerializer(serializers.ModelSerializer):
    remaining_slots = serializers.ReadOnlyField()

    class Meta:
        model = NGOActivity
        fields = '__all__'

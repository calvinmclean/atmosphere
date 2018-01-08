from rest_framework import serializers
from threepio import logger

from django.utils import timezone

from core.models import (AtmosphereUser, EventTable, Instance, InstanceAccess)
from core.serializers.fields import ModelRelatedField
from api.v2.serializers.details import ImageSerializer
from .base import EventSerializer
from .common import AtmosphereUserSerializer
from django.db.models import Sum, Count

class ImageReportSerializer(EventSerializer):
    image = ModelRelatedField(
        lookup_field="provider_alias",
        queryset=Instance.objects.all(),
        serializer_class=InstanceSerializer,
        style={'base_template': 'input.html'})
    user = ModelRelatedField(
        lookup_field="username",
        queryset=AtmosphereUser.objects.all(),
        serializer_class=AtmosphereUserSerializer,
        style={'base_template': 'input.html'})
    timestamp = serializers.DateTimeField(default=timezone.now)
    def validate(self, data):
        raise NotImplemented("This serializer should not be called directly. The sub-class should implement this method.")

class AddImageReportSerializer(ImageReportSerializer)

    def validate(self, data):
        validated_data = data.copy()
        return validated_data

    def save(self):
        # Properly structure the event data as a payload
        serialized_data = self.validated_data
        image_id = serialized_data['image'].provider_alias
        username = serialized_data['user'].username
        timestamp = self.data['timestamp']
        entity_id = image_id
        event_payload = {
            'image_id': image_id,
            'username': username,
            'timestamp': timestamp
        }
        # Create the event in EventTable
        event = EventTable.create_event(
            "report_image",
            event_payload,
            entity_id)
        return event

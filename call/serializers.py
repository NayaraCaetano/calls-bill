from calls_bill_project.serializers import TimestampField

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers, validators

from .models import Call
from .tasks import save_call_record


class CallSerializer(serializers.Serializer):
    call_id = serializers.CharField(required=True)

    def save(self):
        save_call_record.delay(self.validated_data)


class CallDetailStartSerializer(CallSerializer):
    id = serializers.CharField(
        source='start_id',
        required=True,
        validators=[validators.UniqueValidator(queryset=Call.objects.all())]
    )
    timestamp = TimestampField(source='call_start', required=True)
    source = PhoneNumberField(required=True)
    destination = PhoneNumberField(required=True)


class CallDetailEndSerializer(CallSerializer):
    id = serializers.CharField(
        source='end_id',
        required=True,
        validators=[validators.UniqueValidator(queryset=Call.objects.all())]
    )
    timestamp = TimestampField(source='call_end', required=True)

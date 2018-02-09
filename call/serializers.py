from calls_bill_project.serializers import TimestampField

from rest_framework import serializers

from phonenumber_field.serializerfields import PhoneNumberField

from .models import Call


class CallSerializer(serializers.ModelSerializer):
    pass


class CallDetailStartSerializer(CallSerializer):
    id = serializers.CharField(source='start_id', required=True)
    timestamp = TimestampField(source='call_start', required=True)

    class Meta:
        model = Call
        fields = ('id', 'timestamp', 'call_id', 'source', 'destination')
        extra_kwargs = {
            'source': {'required': True},
            'destination': {'required': True}
        }


class CallDetailEndSerializer(CallSerializer):
    id = serializers.CharField(source='end_id', required=True)
    timestamp = TimestampField(source='call_end', required=True)

    class Meta:
        model = Call
        fields = ('id', 'timestamp', 'call_id')

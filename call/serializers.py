from calls_bill_project.serializers import TimestampField

from datetime import date, timedelta
from django.db.models import Sum

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import serializers, validators

from .models import Call
from .tasks import save_call_record


class CallDetailBaseSerializer(serializers.Serializer):
    call_id = serializers.CharField(required=True)

    def save(self):
        save_call_record.delay(self.validated_data)

    def validate(self, data):
        instance = Call.objects.filter(call_id=data['call_id'])
        if instance:
            date_start = instance[0].call_start or data['call_start']
            date_end = instance[0].call_end or data['call_end']
            if date_start > date_end:
                raise serializers.ValidationError('Date end is earlier than date start')
        return data


class CallDetailStartSerializer(CallDetailBaseSerializer):
    id = serializers.CharField(
        source='start_id',
        required=True,
        validators=[validators.UniqueValidator(queryset=Call.objects.all())]
    )
    timestamp = TimestampField(source='call_start', required=True)
    source = PhoneNumberField(required=True)
    destination = PhoneNumberField(required=True)


class CallDetailEndSerializer(CallDetailBaseSerializer):
    id = serializers.CharField(
        source='end_id',
        required=True,
        validators=[validators.UniqueValidator(queryset=Call.objects.all())]
    )
    timestamp = TimestampField(source='call_end', required=True)


class SubscriberBillSerializer(serializers.Serializer):
    subscriber = PhoneNumberField()
    period = serializers.DateField(
        required=False,
        format='%m/%Y',
        input_formats=['%m/%Y', '%m/%y'],
        default=date(
            date.today().year, date.today().month, 1
        ) - timedelta(days=1)
    )
    total_cost = serializers.SerializerMethodField()
    detailed_cost = serializers.SerializerMethodField()

    def validate_period(self, value):
        today = date.today()
        if value.month >= today.month:
            raise serializers.ValidationError(
                'The month does not have a closed period yet'
            )
        return value

    def _get_subscriber_calls(self, data):
        return Call.objects.filter(
            source=data['subscriber'],
            call_start__year=data['period'].year,
            call_start__month=data['period'].month,
        )

    def get_total_cost(self, data):
        subscriber_calls = self._get_subscriber_calls(data)
        return subscriber_calls.aggregate(Sum('cost'))['cost__sum'] or 0.00

    def get_detailed_cost(self, data):
        subscriber_calls = self._get_subscriber_calls(data)
        result = []
        for call in subscriber_calls:
            result.append(CallDetailedSerializer(call).data)
        return result


class CallDetailedSerializer(serializers.ModelSerializer):
    call_start_date = serializers.DateTimeField(
        source='call_start', format='%m/%Y'
    )
    call_start_time = serializers.DateTimeField(
        source='call_start', format='%H:%M:%S'
    )
    call_duration = serializers.DurationField(source='duration')
    call_price = serializers.FloatField(source='cost')

    class Meta:
        model = Call
        fields = (
            'destination', 'call_start_date', 'call_start_time',
            'call_duration', 'call_price'
        )

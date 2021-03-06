import pytz

from datetime import datetime

from rest_framework import serializers


class TimestampField(serializers.DateTimeField):
    """
    Convert a django datetime to/from timestamp.
    """

    def to_internal_value(self, value):
        """
        deserialize a timestamp to a DateTime value
        :param value: the timestamp value
        :return: a django DateTime value
        """
        try:
            value = float(value)
        except ValueError:
            raise serializers.ValidationError(
                'Incorrect format. Expected timestamp string.')

        converted = datetime.utcfromtimestamp(float(value))
        converted = pytz.utc.localize(converted)
        return super(TimestampField, self).to_internal_value(converted)

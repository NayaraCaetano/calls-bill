from calls_bill_project.tests import BaseTestCase

from datetime import datetime

from rest_framework.reverse import reverse_lazy

from parameterized import parameterized

from .models import Call


class CallDetailsTestCase(BaseTestCase):
    URL = reverse_lazy('call_details')

    def _json_call(self, type_call, *args, **kwargs):
        timestamp = str(self.faker.date_time_this_month().timestamp())
        data = {
            'id': kwargs.get('id') or self.faker.pystr(),
            'type': type_call,
            'timestamp': kwargs.get('timestamp') or timestamp,
            'call_id': kwargs.get('call_id') or self.faker.pystr(),
            'source': kwargs.get('source') or '38999999999',
            'destination': kwargs.get('destination') or '3832222222'
        }

        if type_call == 'end':
            del data['source']
            del data['destination']

        return data

    def test_url_does_not_have_auth(self):
        response = self.client.post(self.URL, {})
        self.assertNotEquals(401, response.status_code)

    def test_url_does_not_have_get_method(self):
        response = self.client.get(self.URL)
        self.assertEquals(405, response.status_code)

    def test_url_does_not_have_put_method(self):
        response = self.client.put(self.URL)
        self.assertEquals(405, response.status_code)

    def test_url_des_not_have_delete_method(self):
        response = self.client.delete(self.URL)
        self.assertEquals(405, response.status_code)

    @parameterized.expand(['start', 'end'])
    def test_receive_call_details_return_success(self, type_call):
        response = self.client.post(self.URL, self._json_call(type_call))
        self.assertEquals(201, response.status_code)

    @parameterized.expand([
        ('id', '123a', 'id_start', '123a'),
        ('timestamp', '1517999964.0', 'call_start', datetime(2018, 2, 7, 10, 39, 24)),
        ('source', '38999999999', 'source', '+5538999999999'),
        ('destination', '3832222222', 'destination', '+553832222222')
    ])
    def receive_call_start_saves_correctly(self, json_field, json_field_value, model_field, model_field_value):
        data = self._json_call('start')
        data[json_field] = json_field_value
        self.client.post(self.URL, data)
        obj = Call.objects.get(call_id=data['call_id'])
        self.assertEquals(model_field_value, getattr(obj, model_field))

    @parameterized.expand([
        ('id', '123a', 'id_end', '123a'),
        ('timestamp', '1517999964.0', 'call_start', datetime(2018, 2, 7, 10, 39, 24))
    ])
    def receive_call_end_saves_correctly(self, json_field, json_field_value, model_field, model_field_value):
        data = self._json_call('end')
        data[json_field] = json_field_value
        self.client.post(self.URL, data)
        obj = Call.objects.get(call_id=data['call_id'])
        self.assertEquals(model_field_value, getattr(obj, model_field))

    @parameterized.expand([
        'id',
        'type',
        'timestamp',
        'call_id',
        'source',
        'destination',
    ])
    def test_required_fields_call_start(self, json_field):
        data = self._json_call('start')
        del data[json_field]
        response = self.client.post(self.URL, data)
        self.assertEquals(400, response.status_code)

    @parameterized.expand([
        'id',
        'type',
        'timestamp',
        'call_id',
    ])
    def test_required_fields_call_end(self, json_field):
        data = self._json_call('end')
        del data[json_field]
        response = self.client.post(self.URL, data)
        self.assertEquals(400, response.status_code)

    @parameterized.expand([
        'type',
        'timestamp',
        'source',
        'destination'
    ])
    def test_validate_invalid_data_params(self, json_field):
        data = self._json_call('start')
        data[json_field] = 'invalid'
        response = self.client.post(self.URL, data)
        self.assertEquals(400, response.status_code)

    def test_receive_call_pair_must_calculate_bill(self):
        date_start = datetime(year=2018, month=1, day=1, hour=21, minute=57, second=13)
        date_end = datetime(year=2018, month=1, day=1, hour=22, minute=10, second=56)
        data_start = self._json_call(
            type_call='start',
            timestamp=str(date_start.timestamp()),
            call_id='1'
        )
        data_end = self._json_call(
            type_call='end',
            timestamp=str(date_end.timestamp()),
            call_id='1'
        )

        self.client.post(self.URL, data_start)
        self.client.post(self.URL, data_end)

        obj = Call.objects.get(call_id=data_start['call_id'])
        self.assertEquals(0.54, obj.cost)

    @parameterized.expand(['start', 'end'])
    def test_sending_duplicate_record_must_not_duplicate_on_database(self, type_call):
        data = self._json_call(type_call)
        self.client.post(self.URL, data)
        self.client.post(self.URL, data)
        self.assertEquals(1, Call.objects.all().count())

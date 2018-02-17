import pytest
import pytz

from calls_bill_project.tests import BaseTestCase

from datetime import datetime, date, timedelta

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

    @parameterized.expand([
        (datetime(2018, 1, 1, 21, 57, 13), datetime(2018, 1, 1, 22, 10, 56), 0.54),
        (datetime(2018, 1, 1, 5, 57, 13), datetime(2018, 1, 1, 6, 3, 15), 0.63),
        (datetime(2018, 1, 1, 6, 1, 0), datetime(2018, 1, 1, 6, 3, 15), 0.54),
        (datetime(2018, 1, 1, 5, 57, 0), datetime(2018, 1, 1, 22, 1, 15), 86.76)
    ])
    def test_receive_call_pair_must_calculate_bill(self, date_start, date_end, cost):
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
        self.assertEquals(cost, float(obj.cost))

    @parameterized.expand(['start', 'end'])
    def test_sending_duplicate_record_must_not_duplicate_on_database(self, type_call):
        data = self._json_call(type_call)
        self.client.post(self.URL, data)
        self.client.post(self.URL, data)
        self.assertEquals(1, Call.objects.all().count())

    def test_calc_cost_does_not_run_if_date_start_or_date_end_is_missing(self):
        with pytest.raises(Exception) as excinfo:
            call = self._create_call()
            call.call_end = None
            call.end_id = None
            call.save()
            call.save_cost()
        self.assertEquals(AssertionError, excinfo.type)

    def test_calc_cost_does_not_run_if_date_end_is_earlier_than_date_start(self):
        with pytest.raises(Exception) as excinfo:
            self._create_call(
                call_start=datetime(2018, 1, 1, 12, 0),
                call_end=datetime(2018, 1, 1, 11, 59)
            )
        self.assertEquals(AssertionError, excinfo.type)

    @parameterized.expand([
        (datetime(2018, 1, 1, 22, 57, 13), datetime(2018, 1, 1, 20, 10, 56))
    ])
    def test_must_refuse_date_end_earlyer_than_date_start(self, date_start, date_end):
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
        response = self.client.post(self.URL, data_end)

        self.assertEquals(400, response.status_code)


class CallBillTestCase(BaseTestCase):
    URL = reverse_lazy('call_bill')

    def _queryset_params(self, subscriber, period=''):
        return {
            'subscriber': subscriber,
            'period': period
        }

    def setUp(self):
        super(CallBillTestCase, self).setUp()
        self._create_call(
            source='3199999999',
            call_start=pytz.utc.localize(datetime(2018, 1, 1, 21, 57, 13)),
            call_end=pytz.utc.localize(datetime(2018, 1, 1, 22, 10, 56))
        )
        self._create_call(
            source='3199999999',
            call_start=pytz.utc.localize(datetime(2018, 1, 1, 5, 57, 13)),
            call_end=pytz.utc.localize(datetime(2018, 1, 1, 6, 3, 15))
        )
        self._create_call(
            source='3199999999',
            call_start=pytz.utc.localize(datetime(2017, 12, 1, 5, 57, 13)),
            call_end=pytz.utc.localize(datetime(2017, 12, 1, 6, 3, 15))
        )
        self._create_call(
            source='31988888888',
            call_start=pytz.utc.localize(datetime(2018, 1, 1, 5, 57, 13)),
            call_end=pytz.utc.localize(datetime(2018, 1, 1, 6, 3, 15))
        )

    def test_url_does_not_have_auth(self):
        response = self.client.get(self.URL)
        self.assertNotEquals(401, response.status_code)

    def test_url_does_not_have_post_method(self):
        response = self.client.post(self.URL, {})
        self.assertEquals(405, response.status_code)

    def test_url_does_not_have_put_method(self):
        response = self.client.put(self.URL)
        self.assertEquals(405, response.status_code)

    def test_url_des_not_have_delete_method(self):
        response = self.client.delete(self.URL)
        self.assertEquals(405, response.status_code)

    def test_if_period_not_informed_the_last_month_is_considered(self):
        response = self.client.get(self.URL, self._queryset_params(subscriber='3899999999'))
        period = (date(date.today().year, date.today().month, 1) - timedelta(days=1)).strftime('%m/%Y')
        self.assertEquals(period, response.json()['period'])

    def test_it_is_not_possible_get_bill_for_current_month(self):
        period = (date(date.today().year, date.today().month, 1)).strftime('%m/%Y')
        response = self.client.get(self.URL, self._queryset_params(
            subscriber='3899999999',
            period=period
        ))
        self.assertEquals(400, response.status_code)

    def test_detailed_cost_returns_correct_sum_of_costs(self):
        response = self.client.get(self.URL, self._queryset_params(
            subscriber='3199999999',
            period='01/2018'
        ))
        self.assertEquals(1.17, float(response.json()['total_cost']))

    def test_detailed_cost_only_return_costs_for_period(self):
        response = self.client.get(self.URL, self._queryset_params(
            subscriber='3199999999',
            period='01/2018'
        ))
        detailed = response.json()['detailed_cost']
        self.assertFalse(any(d['call_start_date'] != '01/2018' for d in detailed))

    def test_detailed_cost_only_returns_details_for_subscriber(self):
        response = self.client.get(self.URL, self._queryset_params(
            subscriber='31988888888',
            period='01/2018'
        ))
        detailed = response.json()['detailed_cost']
        self.assertEquals(1, len(detailed))

    def test_incomplete_calls_records_isnt_returned(self):
        self._create_call(
            source='31977888888',
            call_start=pytz.utc.localize(datetime(2018, 1, 1, 5, 57, 13)),
            call_end=None
        )
        response = self.client.get(self.URL, self._queryset_params(
            subscriber='31977888888',
            period='01/2018'
        ))
        detailed = response.json()['detailed_cost']
        self.assertEquals(0, len(detailed))

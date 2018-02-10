import pytz

from call.models import Call

from datetime import datetime, timedelta

from django.test import TestCase

from faker import Faker

from model_mommy.recipe import Recipe, seq

from rest_framework.test import APIClient


class BaseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.faker = Faker('pt_BR')

    def _create_call(self, *args, **kwargs):
        call_start = self.faker.date_time_between(datetime.now() - timedelta(days=1), datetime.now())
        call_end = self.faker.date_time_between(datetime.now(), datetime.now() + timedelta(days=1))

        recipe = Recipe(
            Call,
            call_id=seq('id'),
            start_id=seq('start'),
            end_id=seq('end'),
            call_start=pytz.utc.localize(call_start),
            call_end=pytz.utc.localize(call_end),
            source='3899999999',
            destination='3832222222'
        )
        call = recipe.make(**kwargs)
        call.save_cost()

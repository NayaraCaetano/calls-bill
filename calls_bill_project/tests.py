from django.test import TestCase

from faker import Faker

from rest_framework.test import APIClient


class BaseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.faker = Faker('pt_BR')

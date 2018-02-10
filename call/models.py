from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from .pricing_logic import calc_call_cust


class Call(models.Model):

    call_id = models.CharField(max_length=100, primary_key=True)
    start_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    end_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    call_start = models.DateTimeField(blank=True, null=True)
    call_end = models.DateTimeField(blank=True, null=True)
    source = PhoneNumberField(blank=True, null=True)
    destination = PhoneNumberField(blank=True, null=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)

    def save_cost(self):
        self.cost = calc_call_cust(self.call_start, self.call_end)
        self.save()

    @property
    def duration(self):
        if self.call_end or self.call_start:
            return self.call_end - self.call_start

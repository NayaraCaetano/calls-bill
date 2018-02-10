from django.urls import path

from . import views

urlpatterns = [
    path('details', views.CallDetailsView.as_view(), name='call_details'),
    path('bill', views.CallBillView.as_view(), name='call_bill')
]

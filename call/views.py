from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Call

from .serializers import (
    CallDetailStartSerializer, CallDetailEndSerializer,
    SubscriberBillSerializer
)


class CallDetailsView(CreateAPIView):

    def get_serializer_class(self):
        type_call = self.request.data.get('type', '')
        if type_call.lower() == 'start':
            return CallDetailStartSerializer
        elif type_call.lower() == 'end':
            return CallDetailEndSerializer
        raise ValidationError(
            'Incorrect param "type". Expected "start" or "end".'
        )


class CallBillView(APIView):
    serializer_class = SubscriberBillSerializer

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

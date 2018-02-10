from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ValidationError

from .serializers import CallDetailStartSerializer, CallDetailEndSerializer


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

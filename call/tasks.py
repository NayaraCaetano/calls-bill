from celery import current_app

from call.models import Call


@current_app.task(serializer='pickle')
def save_call_record(data):
    call_id = data.get('call_id')
    Call.objects.update_or_create(
        call_id=call_id,
        defaults=data
    )

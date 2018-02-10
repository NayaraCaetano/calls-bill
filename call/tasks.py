from celery import current_app

from call.models import Call


@current_app.task(serializer='pickle')
def save_call_record(data):
    call_id = data.get('call_id')
    obj, _ = Call.objects.update_or_create(
        call_id=call_id,
        defaults=data
    )
    if obj.start_id and obj.end_id:
        save_record_cost.delay(obj.call_id)


@current_app.task
def save_record_cost(record_id):
    record = Call.objects.get(call_id=record_id)
    record.save_cost()

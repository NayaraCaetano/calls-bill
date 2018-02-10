import pytz

from datetime import time, datetime, timedelta

STANDING_CHARGE = 0.36
RULES = [
    {'start': time(6, 0, 0), 'end': time(22, 0, 0), 'price': 0.09},
    {'start': time(22, 0, 0), 'end': time(23, 59, 59), 'price': 0.00},
    {'start': time(0, 0, 0), 'end': time(6, 0, 0), 'price': 0.00}
]


def calc_call_cust(start, end):
    cost = STANDING_CHARGE
    calls_day = _format_call_in_days_records(start, end)

    _validate_date_interval(start, end)

    for call in calls_day:
        for rule in RULES:
            duration_minutes = _get_rule_duration(
                rule['start'], rule['end'], call['start'], call['end']
            )
            cost = cost + (duration_minutes * rule['price'])
    return cost


def _validate_date_interval(start, end):
    if not start or not end:
        raise AssertionError('No enough data')
    if start > end:
        raise AssertionError('Date end is earlier than date start')


def _format_call_in_days_records(start, end):
    curr = start.replace(hour=0, minute=0, second=0, microsecond=0)
    a_minute = timedelta(minutes=1)
    a_day = timedelta(days=1)
    while curr < end:
        r_start = start if curr < start else curr
        r_end = end if curr + a_day > end else curr + a_day - a_minute
        yield {'start': r_start, 'end': r_end}
        curr += a_day


def _get_rule_duration(rule_start, rule_end, start, end):
    date_rule_start = pytz.utc.localize(
        datetime.combine(start.date(), rule_start)
    )
    date_rule_end = pytz.utc.localize(
        datetime.combine(start.date(), rule_end)
    )

    is_inside_start = start >= date_rule_start and start < date_rule_end
    is_inside_end = end < date_rule_end and end >= date_rule_start
    is_outside_start = start < date_rule_start
    is_outside_end = end >= date_rule_end

    if is_inside_start and is_inside_end:
        duration = datetime_to_minutes(end - start)

    elif is_outside_start and is_outside_end:
        duration = datetime_to_minutes(date_rule_end - date_rule_start)

    elif is_outside_start and is_inside_end:
        duration = datetime_to_minutes(end - date_rule_start)

    elif is_inside_start and is_outside_end:
        duration = datetime_to_minutes(date_rule_end - start)
    else:
        duration = 0

    return duration


def datetime_to_minutes(date_time):
    try:
        return int(date_time.strftime('%s'))//60
    except AttributeError:
        return date_time.total_seconds()//60

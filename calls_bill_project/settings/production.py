from .base import *

import dj_database_url


DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '.herokuapp.com']

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)


CELERY_REMAP_SIGTERM = 'SIGQUIT celery -A calls_bill_project worker -l info'
CELERY_DEFAULT_QUEUE = 'work-at-olist-celery'
CELERY_BROKER_TRANSPORT_OPTIONS['queue_name_prefix'] = 'work-at-olist-'

RAVEN_CONFIG = {
    'dsn': 'https://673caaff9b84413fa7d8141ef1665ebb:70e02a2683224b49a9606299c35f327f@sentry.io/285375',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(name)s - %(levelname)s'
                      ' - %(process)d - %(thread)d - %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat'
                     '.handlers.SentryHandler',
        },
    },
    'loggers': {
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'oc.storage': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'tasks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'level': 'DEBUG',
            'handlers': ['sentry', 'console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'boto3.resources.collection': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'botocore.vendored.requests.packages.urllib3.connectionpool': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        }
    },
}

from .base import *


TEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

CELERY_TASK_ALWAYS_EAGER = True

from .celeryconfig_local import *
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ('json', )
CELERY_TASK_IGNORE_RESULT = True
CELERY_BEAT_SCHEDULE = {
    'update-every-30-seconds': {
        'task': 'leomaster_app.tasks.update',
        'schedule': 300.0,
        'args': tuple()
    },
}


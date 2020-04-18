from leomaster.celeryconfig_local import *
from kombu import Queue, Exchange
from celery.schedules import crontab
from core.settings import LEO_TASK_EXPIRES

timezone = 'UTC'
enable_utc = True
accept_content = ('json',)
task_ignore_result = True
task_create_missing_queues = False
task_default_queue = 'celery'


task_queues = (Queue(name='celery', exchange=Exchange('celery'), routing_key='celery'),
               Queue(name='updates', exchange=Exchange('updates'), routing_key='updates'),
               Queue(name='downloads', exchange=Exchange('downloads'), routing_key='downloads'),
               Queue(name='notifications', exchange=Exchange('notifications'), routing_key='notifications'))

task_routes = {'core.tasks.update': {'queue': 'updates'},
               'core.tasks.update_images': {'queue': 'updates'},
               'core.tasks.download_images': {'queue': 'downloads'},
               'core.tasks.notify': {'queue': 'notifications'}, }

beat_schedule = {
    'update-every-30-seconds': {
        'task': 'core.tasks.update',
        'schedule': 300.0,
        'args': tuple(),
        'options': {
            'expires': LEO_TASK_EXPIRES,
            'queue': 'updates'
        }
    },
    'update-img-everyday-at-midnight': {
        'task': 'core.tasks.update_images',
        'schedule': crontab(minute=0, hour=0),
        'args': tuple(),
        'options': {
            'expires': LEO_TASK_EXPIRES,
            'queue': 'updates'
        }
    },
    'watchdog-everyday': {
        'task': 'core.tasks.watchdog',
        'schedule': crontab(minute=0, hour=10),
        'args': tuple(),
        'options': {
            'queue': 'updates'
        }
    }
}


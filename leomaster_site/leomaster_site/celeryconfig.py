from .celeryconfig_local import *

CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ('json', )
CELERY_TASK_IGNORE_RESULT = True


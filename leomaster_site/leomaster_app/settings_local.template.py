import os
from django.conf import settings

LEO_TASK_LOG_PATH = '../log/task.log'
LEO_TASK_LOG_LEVEL = 'DEBUG'
LEO_PARSER_CONFIG_PATH = os.path.join(settings.BASE_DIR, '../leoparser/parser_config.json')
LEO_RETRY_DELAY = '60'
LEO_UPDATE_PERIOD = '5'

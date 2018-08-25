import os
import fake_useragent
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leomaster_site.settings')

LEO_TELEGRAM_MODE = 'HTML'
LEO_TELEGRAM_BOT_TOKEN = '<token>'
LEO_TELEGRAM_CHAT_ID = '<chat_id>'
LEO_TELEGRAM_ADMIN_CHAT_ID = '<admin_chat_id>'
LEO_TASK_LOG_PATH = '../log/task.log'
LEO_TASK_LOG_LEVEL = 'DEBUG'
LEO_PARSER_CONFIG_PATH = os.path.join(settings.BASE_DIR, '../leoparser/parser_config.json')
LEO_RETRY_DELAY = 60
LEO_UPDATE_PERIOD = 5
LEO_DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
LEO_FAKE_USER_AGENT_CACHE = os.path.join(settings.BASE_DIR, '../fake_useragent%s.json' % fake_useragent.VERSION)
LEO_TASK_EXPIRES = 300
LEO_TASK_TIMEOUT = 30
LEO_NOTIFICATION_MAX_RETRIES = 100
LEO_DOWNLOAD_MAX_RETRIES = 1
LEO_UPDATE_MAX_RETRIES = 1

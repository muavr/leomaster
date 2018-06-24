import requests
from leobot.settings import *


class LeoBot:
    def __init__(self, token, token_prefix='', api_url=''):
        self.token = token
        self.token_prefix = token_prefix if token_prefix else TELEGRAM_TOKEN_PREFIX
        self.api_url = api_url if api_url else TELEGRAM_API_URL

    def _build_cmd_url(self, cmd):
        token = '{0}{1}'.format(self.token_prefix, self.token)
        url = '/'.join(s.strip('/') for s in (self.api_url, token, cmd) if s)
        return url

    def send_message(self, chat_id, text, mode='HTML'):
        cmd = 'sendMessage'
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': mode}
        url = self._build_cmd_url(cmd)
        return requests.post(url, data=payload)










import pytz
import time
import json
import random
import requests
import celery.signals

from django.conf import settings
from datetime import datetime, timedelta
from django.template import loader
from django.utils import translation
from django.utils.formats import date_format
from celery.utils.log import get_task_logger
from logging.handlers import TimedRotatingFileHandler

from leobot.bot import LeoBot
from leomaster_app.models import *
from leomaster_app.settings import *
from leomaster_site.celery import app
from leoparser.leoparser import LeoParserFabric

CONTENT_URL = 'https://leonardo.ru/masterclasses/petersburg/'
CURRENT_TZ = 'Europe/Moscow'

logger = get_task_logger(__name__)


@celery.signals.after_setup_task_logger.connect
def on_after_setup_task_logger(**kwargs):
    def_logger = kwargs.get('logger', None)
    if def_logger:
        stream_handler = def_logger.handlers[1]
        def_logger.removeHandler(stream_handler)
        time_rot_fh = TimedRotatingFileHandler(filename=LEO_TASK_LOG_PATH, encoding='utf-8',
                                               when='d', interval=10, backupCount=15)
        time_rot_fh.setLevel(LEO_TASK_LOG_LEVEL)
        time_rot_fh.setFormatter(stream_handler.formatter)
        def_logger.addHandler(time_rot_fh)


@app.task(bind=True, ignore_result=True)
def update(self):
    random.seed()
    time.sleep(random.randint(0, 120))
    logger.info('Starting update task')
    user_agent = fake_useragent.UserAgent(fallback=LEO_DEFAULT_USER_AGENT,
                                          path=LEO_FAKE_USER_AGENT_CACHE)
    current_agent = user_agent.random
    logger.info('Current user agent: {0}'.format(current_agent))

    http_headers = {'User-Agent': current_agent}
    web_session = requests.Session()
    web_request = requests.Request('GET', CONTENT_URL, headers=http_headers)
    prepared_request = web_request.prepare()
    logger.info('Executing HTTP request (url: "{0}")'.format(CONTENT_URL))
    try:
        response = web_session.send(prepared_request)
    except requests.RequestException as err:
        logger.exception(err)
        logger.warning('Task will be retried after {0} sec'.format(LEO_RETRY_DELAY))
        raise self.retry(exc=err, countdown=LEO_RETRY_DELAY)

    logger.info('Open parser config file: "{0}"'.format(LEO_PARSER_CONFIG_PATH))
    with open(LEO_PARSER_CONFIG_PATH, 'r', encoding='utf8') as f_dsc:
        config = f_dsc.read()
        f_dsc.close()
        logger.info('Config file closed')
    config_dict = json.loads(config)
    lp_fabric = LeoParserFabric(config_dict)
    logger.info('Creating parser')
    lp = lp_fabric.create_parser()
    logger.info('Extracting page content (encoding: {0})'.format(response.encoding))
    raw_content = response.content.decode(encoding=response.encoding).encode(encoding='utf-8').decode(encoding='utf-8')
    logger.info('Parsing'.format())
    parsed_content = lp.parse_to_dict(raw_content)
    for key, body in parsed_content.items():
        logger.info('Masterclass has been found (uid: {0})'.format(key))
        master, created = Master.objects.get_or_create(name=body.pop('master', ''))
        if created:
            logger.info('New master was added: "{0}"'.format(master.name))
        else:
            logger.info('Master already exists: "{0}"'.format(master.name))

        location, created = Location.objects.get_or_create(name=body.pop('location', ''))
        if created:
            logger.info('New location was added: "{0}"'.format(location.name))
        else:
            logger.info('Location already exists: "{0}"'.format(location.name))

        if not Masterclass.objects.filter(uid=key).exists():
            mc = Masterclass.objects.create(**body, master=master, location=location)
            logger.info('New masterclass was added: "{0}"'.format(mc.uid))
            download_images.delay(mc.id)
            notify.delay(mc.id)
        else:
            logger.info('Masterclass already exists: "{0}"'.format(key))

    logger.info('Update task finished%s%s%s' % ('\n', '=' * 25, '\n'))


def download_image(url, http_headers, web_session):
    request = requests.Request('GET', url, headers=http_headers)
    prepared_request = request.prepare()
    logger.info('Downloading image (url: "{0}")'.format(url))
    response = web_session.send(prepared_request)
    if response.status_code == 200:
        return response.content
    return None


def save_binary(content, path):
    with open(path, 'wb') as f:
        f.write(content)
        f.close()


@app.task(bind=True, max_retries=0, ignore_result=True)
def update_images(self):
    _2_month_ago = datetime.today() - timedelta(days=30)
    masterclasses = Masterclass.objects.all().filter(creation_ts__gte=_2_month_ago)
    for mc in masterclasses:
        download_images.delay(mc.id)


@app.task(bind=True, max_retries=1, ignore_result=True, default_retry_delay=60*2.5)
def download_images(self, mc_id):
    logger.info('Starting download task')
    logger.info('Downloading images for masterclass id= {0}'.format(mc_id))
    user_agent = fake_useragent.UserAgent(fallback=LEO_DEFAULT_USER_AGENT,
                                          path=LEO_FAKE_USER_AGENT_CACHE)
    current_agent = user_agent.random
    logger.info('Current user agent: {0}'.format(current_agent))

    http_headers = {'User-Agent': current_agent}
    web_session = requests.Session()

    mc = Masterclass.objects.get(pk=mc_id)
    target_dir = os.path.join(settings.MEDIA_ROOT, settings.DOWNLOAD_IMG_DIR)
    logger.debug('Target directory is "{0}"'.format(target_dir))

    try:
        url = 'https:' + mc.img_url
        img_content = download_image(url, http_headers, web_session)
        img_path = os.path.join(target_dir, '{0}.jpeg'.format(mc.uid))
        save_binary(img_content, img_path)

        url = 'https:' + mc.preview_img_url
        img_content = download_image(url, http_headers, web_session)
        img_path = os.path.join(target_dir, '{0}_preview.jpeg'.format(mc.uid))
        save_binary(img_content, img_path)

    except requests.RequestException as err:
        print(err)
        logger.exception(err)
        logger.warning('Task will be retried after {0} sec'.format(LEO_RETRY_DELAY))
        raise self.retry(exc=err, countdown=LEO_RETRY_DELAY)


@app.task(bind=True, max_retries=20, ignore_result=True, default_retry_delay=60*2.5)
def notify(self, mc_id):
    translation.activate('ru')
    leobot = LeoBot(LEO_TELEGRAM_BOT_TOKEN)
    mc = Masterclass.objects.get(pk=mc_id)
    template = loader.get_template('leomaster_app/telegram_notification.html')
    context = {'title': mc.title,
               'when': date_format(mc.date.astimezone(pytz.timezone(mc.location.tz)), 'd-m-Y H:i, l'),
               'where': mc.location.name,
               'who': mc.master.name,
               'howmany': mc.avail_seats,
               'preview': '//{0}/media/downloads/img/{1}_preview.jpeg'.format(settings.ALLOWED_HOSTS[0],  mc.uid),
               'online_price': mc.online_price,
               'price': mc.price,
               'description': mc.description,
               'target': CONTENT_URL}
    rendered = template.render(context=context)
    leobot.send_message(LEO_TELEGRAM_CHAT_ID, rendered)

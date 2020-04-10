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
from _leoparser.leoparser import LeoParserFabric

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


@app.task(bind=True, max_retries=LEO_UPDATE_MAX_RETRIES, ignore_result=True)
def update(self):
    random.seed()
    time.sleep(random.randint(0, 120))
    logger.info('>>>>> Starting update task')
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
        response = web_session.send(prepared_request, timeout=LEO_TASK_TIMEOUT)
    except requests.RequestException as err:
        logger.exception('Error occurred while trying to update masterclasses: {0}'.format(err))
        logger.warning('Task "download_images" will be retry (attempt {0} of {1})'.format(
            self.request.retries, LEO_DOWNLOAD_MAX_RETRIES))
        raise self.retry(exc=err, countdown=(2 ** self.request.retries) * LEO_RETRY_DELAY)

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

            chain = celery.chain(
                download_images.si(mc.id).set(queue='downloads'),
                notify.si(mc.id).set(queue='notifications'),
            )
            chain.delay()
        else:
            body.pop('uid')
            if body.get('duration') == 0:
                body.pop('duration')
            body = {key: value for key, value in body.items() if value not in {'', None}}
            Masterclass.objects.filter(uid=key).update(**body, master=master, location=location)
            logger.info('Masterclass already exists: "{0}"'.format(key))

    logger.info('<<<<< Update task finished')


def download_image(url, http_headers, web_session):
    request = requests.Request('GET', url, headers=http_headers)
    prepared_request = request.prepare()
    response = web_session.send(prepared_request, timeout=LEO_TASK_TIMEOUT)
    if response.status_code == 200:
        return response.content
    logger.warning('Problem occurred while downloading image "{0}", response code is {1}'.format(
        url, response.status_code))
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
        download_images.apply_async(args=(mc.id,), queue='updates')


@app.task(bind=True, max_retries=LEO_DOWNLOAD_MAX_RETRIES, ignore_result=True, expires=LEO_TASK_EXPIRES)
def download_images(self, mc_id):
    logger.info('>>>>> Mc {0}: Downloading images'.format(mc_id))
    user_agent = fake_useragent.UserAgent(fallback=LEO_DEFAULT_USER_AGENT,
                                          path=LEO_FAKE_USER_AGENT_CACHE)
    current_agent = user_agent.random
    logger.info('Mc {0}: Current user agent: {1}'.format(mc_id, current_agent))

    http_headers = {'User-Agent': current_agent}
    web_session = requests.Session()

    mc = Masterclass.objects.get(pk=mc_id)
    target_dir = os.path.join(settings.MEDIA_ROOT, settings.DOWNLOAD_IMG_DIR)
    logger.debug('Mc {0}: Target directory is "{1}"'.format(mc_id, target_dir))

    try:
        url = 'https:' + mc.img_url
        logger.info('Mc {0}: Downloading main image "{1}"'.format(mc_id, url))
        img_content = download_image(url, http_headers, web_session)
        if img_content is None:
            return
        img_path = os.path.join(target_dir, '{0}.jpeg'.format(mc.uid))
        save_binary(img_content, img_path)
        logger.info('Mc {0}: Image saved to {1}'.format(mc_id, img_path))

        url = 'https:' + mc.preview_img_url
        logger.info('Mc {0}: Downloading preview image "{1}"'.format(mc_id, url))
        img_content = download_image(url, http_headers, web_session)
        if img_content is None:
            return
        img_path = os.path.join(target_dir, '{0}_preview.jpeg'.format(mc.uid))
        save_binary(img_content, img_path)
        logger.info('Mc {0}: Image saved to {1}'.format(mc_id, img_path))
    except requests.RequestException as err:
        logger.exception('Mc {0}: Error occurred while trying to download image: {1}'.format(mc_id, err))
        logger.warning('Mc {0}: Task "download_images" will be retry (attempt {1} of {2})'.format(
            mc_id, self.request.retries, LEO_DOWNLOAD_MAX_RETRIES))
        raise self.retry(exc=err, countdown=(2 ** self.request.retries) * LEO_RETRY_DELAY)
    finally:
        logger.info('<<<<< Mc {0}:  Downloading images finished'.format(mc_id))


@app.task(bind=True, max_retries=LEO_NOTIFICATION_MAX_RETRIES, ignore_result=True)
def notify(self, mc_id):
    lang = 'ru'
    logger.info('>>>>> Mc {0}: Notify about masterclass'.format(mc_id))
    translation.activate(lang)
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
    logger.debug('Mc {0}: Template context: {1}'.format(mc_id, context))
    rendered = template.render(context=context)
    try:
        logger.debug('Mc {0}: Try send message'.format(mc_id))
        leobot.send_message(LEO_TELEGRAM_CHAT_ID, rendered)
    except Exception as err:
        logger.exception('Mc {0}: Error occurred while trying to send message: {1}'.format(mc_id, err))
        logger.warning('Mc {0}: Task "notify" will be retry (attempt {1} of {2})'.format(
            mc_id, self.request.retries, LEO_NOTIFICATION_MAX_RETRIES))
        raise self.retry(exc=err, countdown=(2 ** self.request.retries) * LEO_RETRY_DELAY)
    finally:
        logger.info('<<<<< Mc {0}:  Notifying finished'.format(mc_id))


@app.task(bind=True, max_retries=0, ignore_result=True, expires=LEO_TASK_EXPIRES)
def watchdog(self):
    logger.info('>>>>> Watchdog starting')
    leobot = LeoBot(LEO_TELEGRAM_BOT_TOKEN)
    try:
        today = date_format(datetime.now(tz=pytz.timezone(CURRENT_TZ)), 'd-m-Y H:i, l'),
        logger.info('Watchdog say: ' + str(today))
        leobot.send_message(LEO_TELEGRAM_ADMIN_CHAT_ID, 'Watchdog say: ' + str(today))
    except Exception as err:
        logger.exception('Error occurred while trying to watchdog: {0}'.format(err))
    finally:
        logger.info('<<<<< Watchdog finished')

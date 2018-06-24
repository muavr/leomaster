import json
import requests
import fake_useragent

from celery.utils.log import get_task_logger

from leomaster_app.models import *
from leomaster_app.settings import *
from leomaster_site.celery import app
from leoparser.leoparser import LeoParserFabric

CONTENT_URL = 'https://leonardo.ru/masterclasses/petersburg/'

logger = get_task_logger(__name__)


@app.task(bind=True)
def update(self):
    logger.info('Starting update task')
    user_agent = fake_useragent.UserAgent()
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
        else:
            logger.info('Masterclass already exists: "{0}"'.format(key))

    logger.info('Update task finished%s%s%s' % ('\n', '=' * 25, '\n'))

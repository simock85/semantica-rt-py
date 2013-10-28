import logging
import facebook
from gevent.pool import Pool
import redis
from semantica_rt_py.persistence_config import redis_pool, mongodb

try:
    import simplejson as json
except ImportError:
    import json
import gevent

__author__ = 'simock85'

log = logging.getLogger(__name__)

FETCHERS_POOL = Pool(size=200)


def tokenize_message(message):
    changes = (dict(page_id=entry['id'], **change) for entry in message['entry'] for change in entry['changes'] if \
               change['value']['item'] == 'status')
    return changes


def sync_fetch_fb_data(change):
    log.debug('sync fetch')
    page = mongodb.pages.find_one({'page_id': change['page_id']})
    user_token = page['user_token']
    graph = facebook.GraphAPI(user_token)
    item_id = change['value']['post_id']
    fb_data = graph.get_object(item_id)
    change.update({'fb_data': fb_data, 'already_sent': 0})
    mongodb.updates.insert(change)


def spawn_fetchers(message):
    changes = tokenize_message(message)
    log.debug(changes)
    for change in changes:
        FETCHERS_POOL.spawn(sync_fetch_fb_data, change)


class RedisSucker(object):
    def connect_handler(self):
        for retry in range(3):
            try:
                self.redis_client = redis.Redis(connection_pool=redis_pool)
                self.redis_client.ping()
            except redis.ConnectionError:
                gevent.sleep(5)
                continue
            else:
                return
        raise redis.ConnectionError

    def start(self):
        self.connect_handler()
        while True:
            try:
                message = self.redis_client.brpop('messages')
                message = json.loads(message[1])
                log.debug('received')
                spawn_fetchers(message)
            except redis.ConnectionError:
                self.connect_handler()
            except Exception as e:
                log.exception('Message error')


def init_redis_sucker(event):
    sucker = RedisSucker()
    greenlet = gevent.Greenlet(sucker.start)
    greenlet.start()

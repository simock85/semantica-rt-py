from urlparse import urlparse
import pymongo
from pymongo.errors import CollectionInvalid
from redis import ConnectionPool

__author__ = 'simock85'

MONGO_URI = 'mongodb://semantica:semantica@paulo.mongohq.com:10004/semantica_rt'
REDIS_URI = 'redis://pub-redis-17169.us-east-1-3.1.ec2.garantiadata.com:17169'


class ConfigurationError(Exception):
    pass


try:
    _dbname = urlparse(MONGO_URI).path[1:]
except:
    _dbname = 'semantica_rt'

_connection = pymongo.Connection(MONGO_URI)
mongodb = _connection[_dbname]

try:
    mongodb.create_collection('pages')
    mongodb.create_collection('updates')
except CollectionInvalid:
    pass

mongodb.pages.ensure_index('page_id')
mongodb.updates.ensure_index([('already_sent', pymongo.ASCENDING), ('page_id', pymongo.ASCENDING)])


def create_redis_pool(event):
    def parse_url(**kwargs):
        url = urlparse(kwargs['host'])
        if url.scheme != 'redis':
            raise ConfigurationError('Invalid redis uri scheme: %s' % url.scheme)
        db = kwargs.pop('db')
        if not db:
            try:
                db = int(url.path.replace('/', ''))
            except (AttributeError, ValueError):
                db = 0
        kwargs.update({'host': url.hostname, 'port': int(url.port or 6379),
                       'db': db, 'password': url.password})
        return kwargs

    kwargs = {
        'host': REDIS_URI,
        'db': 0,
        'max_connections': 5
    }

    kwargs = parse_url(**kwargs)
    return ConnectionPool(**kwargs)


redis_pool = create_redis_pool(REDIS_URI)

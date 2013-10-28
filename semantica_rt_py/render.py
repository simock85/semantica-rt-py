from bson import json_util

__author__ = 'simock85'


def bson_renderer(helper):
    return _BsonRenderer()


class _BsonRenderer(object):
    def __call__(self, data, context):
        acceptable = ('application/json', 'text/json', 'text/plain')
        response = context['request'].response
        content_type = (context['request'].accept.best_match(acceptable)
                        or acceptable[0])
        response.content_type = content_type
        if hasattr(data, '__json__'):
            data = data.__json__()
        return json_util.dumps(data)


def includeme(config):
    config.add_renderer('bson', bson_renderer)
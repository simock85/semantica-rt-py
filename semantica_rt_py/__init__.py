from gevent.monkey import patch_all
patch_all()
from pyramid.config import Configurator
from semantica_rt_py import persistence_config
from semantica_rt_py.queue_subscriber import init_redis_sucker
from pyramid.events import ApplicationCreated


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include("cornice")
    config.include('semantica_rt_py.renderer')
    config.add_subscriber(init_redis_sucker, ApplicationCreated)
    config.scan("semantica_rt_py.views")
    return config.make_wsgi_app()

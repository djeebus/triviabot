import click
import logging
import logging.config
import yaml

from multiprocessing.process import Process
from time import sleep


@click.command()
@click.argument('config', type=click.File())
def cli(config):
    _configure_logging()

    config = yaml.load(config)

    for plugin_config in config['plugins']:
        plugin_config['redis'] = config['redis']
        _launch(plugin_config['type'], plugin_config, False)

    sleep(3)  # wait for plugins to subscribe to queues

    from triviabot.daemon import Daemon
    core_config = config['core']
    core_config['redis'] = config['redis']
    daemon = Daemon(core_config)

    p = Process(target=daemon.run)
    p.daemon = True
    p.run()

    while True:
        sleep(1)


def _launch(type_name, config, is_important):
    plugin_clazz = _get_type(type_name)
    if not plugin_clazz:
        logging.warn('could not find %s plugin' % type_name)

    d = plugin_clazz(config)

    p = Process(target=d.start)
    p.daemon = not is_important
    p.name = 'plugin: %s' % d.name
    p.start()


def _get_type(type_name):
    module_name, clazz_name = type_name.rsplit('.', 1)
    module = __import__(module_name,
                        fromlist=module_name.rsplit('.', 1))
    clazz = getattr(module, clazz_name)
    return clazz


def _configure_logging():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'generic': {
                'format': '%(threadName)s %(levelname)s [%(name)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'generic',
            }
        },
        'keys': {
            'request': {
                'level': 'INFO',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': [
                'console',
            ]
        },
    })


if __name__ == '__main__':
    cli()

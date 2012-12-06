from __future__ import unicode_literals, print_function

from functools import partial
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


config = configparser.ConfigParser()
config.read('config.ini')

redis = partial(config.get, 'redis')
redisint = partial(config.getint, 'redis')


def twitter(key):
    return config.get('twitter', key).decode('utf-8')

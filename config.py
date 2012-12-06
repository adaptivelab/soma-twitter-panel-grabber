from __future__ import unicode_literals, print_function

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


config = configparser.ConfigParser()
config.read('config.ini')


def twitter(key):
    return config.get('twitter', key).decode('utf-8')

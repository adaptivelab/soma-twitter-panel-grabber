"""
For dealing with source data for decided which twitter accounts to scrape
"""

from __future__ import unicode_literals, print_function

import time
import redis
import logging
import json

import config


logger = logging.getLogger('wood_panelling')


class RedisStorage(object):

    def __init__(self):
        self.db = redis.StrictRedis(
            host=config.redis('host'),
            port=config.redisint('port'),
            db=config.redisint('db')
        )

    def key_for(self, *args):
        return ':'.join(args)

    def store_profile(self, profile):
        key = self.key_for('profile', profile['screen_name'])
        date_key = self.key_for(key, 'last-fetched')
        logger.info('storing {}'.format(key))
        self.db[key] = json.dumps(profile)
        self.db[date_key] = time.time()
        self.db.sadd('profiles', profile['screen_name'])

    def store_followers(self, screen_name, follower_list):
        key = self.key_for('followers', screen_name)
        date_key = self.key_for(key, 'last-fetched')
        logger.info('storing {} items in {}'.format(len(follower_list), key))
        self.db.rpush(key, *follower_list)
        self.db[date_key] = time.time()

    def store_friends(self, screen_name, friends_list):
        key = self.key_for('friends', screen_name)
        date_key = self.key_for(key, 'last-fetched')
        logger.info('storing {} items in {}'.format(len(friends_list), key))
        self.db.rpush(key, *friends_list)
        self.db[date_key] = time.time()


class LoggingStorage(object):

    def store_profile(self, profile):
        logger.info("storing profile: {}".format(profile['screen_name']))

    def store_followers(self, screen_name, follower_list):
        logger.info("{} is followed by {}".format(screen_name, follower_list))

    def store_friends(self, screen_name, friends_list):
        logger.info("{} is friends with {}".format(screen_name, friends_list))


def load_source(filename):
    with open(filename) as io:
        return list(line.strip() for line in io)

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

    def push_list(self, key, lst):
        for id in lst:
            self.db.rpush(key, id)

    def keys_for(self, *args):
        key = self.key_for(*args)
        return key, self.key_for(key, 'last-fetched')

    def store_profile(self, profile):
        key, date_key = self.keys_for('profile', profile['screen_name'])
        logger.info('storing {}'.format(key))
        self.db[key] = json.dumps(profile)
        self.db[date_key] = time.time()
        self.db.sadd('profiles', profile['screen_name'])

    def store_followers(self, screen_name, follower_list):
        key, date_key = self.keys_for('followers', screen_name)
        logger.info('storing {} items in {}'.format(len(follower_list), key))
        self.push_list(key, follower_list)
        self.db[date_key] = time.time()

    def store_friends(self, screen_name, friends_list):
        key, date_key = self.keys_for('friends', screen_name)
        logger.info('storing {} items in {}'.format(len(friends_list), key))
        self.push_list(key, friends_list)
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

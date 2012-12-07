"""
For dealing with source data for decided which twitter accounts to scrape
"""

from __future__ import unicode_literals, print_function

import time
import redis
import logging
import json
import datetime

import config


logger = logging.getLogger('wood_panelling')


class RedisDataStore(object):
    """
    Store and read data from redis based on config

    plus some helpers to get around ancient redis verion and limited api
    """

    def __init__(self):
        self.db = redis.StrictRedis(
            host=config.redis('host'),
            port=config.redisint('port'),
            db=config.redisint('db')
        )

    def push_list(self, key, lst):
        for id in lst:
            self.db.rpush(key, id)

    def timestamp(self, key):
        return datetime.datetime.fromtimestamp(float(self.db[key]))

    def key_for(self, *args):
        return ':'.join(args)

    def keys_for(self, *args):
        key = self.key_for(*args)
        return key, self.key_for(key, 'last-fetched')


class RedisSource(RedisDataStore):
    """
    Read panel information from redis and shape it into
    a format useful for SoMA
    """

    @property
    def screen_names(self):
        return self.db.smembers('profiles')

    def profile(self, screen_name):
        key, date_key = self.keys_for('profile', screen_name)
        profile = json.loads(self.db[key])
        return profile, self.timestamp(date_key)

    def _collection(self, collection, screen_name):
        key, date_key = self.keys_for(collection, screen_name)
        return self.db.lrange(key, 0, -1), self.timestamp(date_key)

    def followers(self, screen_name):
        return self._collection('followers', screen_name)

    def friends(self, screen_name):
        return self._collection('friends', screen_name)


class RedisStorage(RedisDataStore):
    """
    Store fetched twitter panel data in redis based on config
    """

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

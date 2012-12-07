"""
For dealing with source data for decided which twitter accounts to scrape
"""

from __future__ import unicode_literals, print_function

import redis
import logging
import json
import datetime
import time
import rfc822
import calendar  #python's date handling is crazy

import config


logger = logging.getLogger('wood_panelling')

TWITTER_KEYS = [
    "id",
    "name",
    "screen_name",
    "statuses_count",
    "description",
    "url",
    "time_zone",
    "lang",
    "location",
    "profile_image_url",
    "followers_count",
    "friends_count",
]


def datestr_to_timestamp(date_str):
    """
    parse a rfc822 date to a timestamp

    >>> datestr_to_timestamp('Sat Jan 10 06:11:29 +0000 2000')
    947484689
    """

    timetuple = rfc822.parsedate(date_str)
    return calendar.timegm(timetuple)

def mongo_timestamp(seconds):
    """
    return a dict that looks like a mongo json date

    >>> mongo_timestamp(947484689)
    {u'$date': 947484689000}
    >>> mongo_timestamp(datetime.datetime(2000, 1, 10, 6, 11, 29))
    {u'$date': 947484689000}
    >>> mongo_timestamp('Sat Jan 10 06:11:29 +0000 2000')
    {u'$date': 947484689000}
    """
    if isinstance(seconds, datetime.datetime):
        seconds = time.mktime(seconds.utctimetuple())
    elif isinstance(seconds, basestring):
        seconds = datestr_to_timestamp(seconds)
    return {'$date': int(seconds*1000)}


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

    def panelist_info(self, screen_name):
        profile, profile_updated = self.profile(screen_name)
        panelist = {key: profile[key] for key in TWITTER_KEYS}
        panelist['created_at'] = mongo_timestamp(profile['created_at'])
        panelist['last_fetched'] = mongo_timestamp(profile_updated)
        followers, followers_updated = self.followers(screen_name)
        panelist['followers'] = {
            'last_fetched': mongo_timestamp(followers_updated),
            'ids': followers
        }
        friends, friends_updated = self.friends(screen_name)
        panelist['friends'] = {
            'last_fetched': mongo_timestamp(friends_updated),
            'ids': friends
        }
        return {
            'twitter': panelist,
        }


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

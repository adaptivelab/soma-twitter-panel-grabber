"""
For dealing with source data for decided which twitter accounts to scrape
"""

from __future__ import unicode_literals, print_function

import logging

import config


logger = logging.getLogger('wood_panelling')


class RedisStorage(object):

    def __init__(self):
        self.id_map = {}
        self.follower_map = defaultdict(list)
        self.friends_map = defaultdict(list)

    def store_profile(self, profile):
        pass

    def store_followers(self, screen_name, follower_list):
        pass

    def store_friends(self, screen_name, friends_list):
        pass


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

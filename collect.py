# encoding: utf-8
"""
Update a SoMA panel from a source file of panelists
"""

from __future__ import unicode_literals, print_function

import sys
import multiprocessing
import logging
from collections import defaultdict
import time

import source
import client

logger = logging.getLogger('wood_panelling')


def twitter_uri(group, method):
    """
    Get full uri for api endpoint
    """

    return "https://api.twitter.com/1.1/{}/{}.json".format(group, method)


class UnexpectedError(Exception):
    """
    Well that was interesting…
    """


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


def fetch(client, screen_names, storage):
    """
    Set up and run separate processes for fetching each of:
    profiles, followers and friends adding them to the storage object
    """

    args = (client, screen_names, storage)
    profiles = multiprocessing.Process(target=fetch_profiles, args=args)
    followers = multiprocessing.Process(target=fetch_followers, args=args)
    friends = multiprocessing.Process(target=fetch_friends, args=args)
    logger.info("starting collection")
    [p.start() for p in [profiles, followers, friends]]
    [p.join() for p in [profiles, followers, friends]]
    logger.info("finished collection")


def fetch_profiles(client, screen_names, storage):
    """
    Fetch twitter profile information for screen_names and add them to storage

    Can request 100 profiles per request and 180 requests per 15mins
    """

    lookup_uri = twitter_uri('users', 'lookup')
    size_limit = 100

    while screen_names:
        clump = screen_names[:size_limit]
        response = client.get(lookup_uri,
            params={'screen_name': ",".join(clump)})
        if ok(response):
            del screen_names[:size_limit]
            for profile in response.json:
                storage.store_profile(profile)
            logger.debug("fetched 100 profiles, %d left" % len(screen_names))
        elif rate_limited(response):
            # rate limiting, need to sleep
            client.wait_for(lookup_uri)
        else:
            raise UnexpectedError(response.status_code, response.text)
        client.enhance_my_calm()


def fetch_followers(client, screen_names, storage):
    """
    Fetch followers for all screen_names and store in storage object
    """

    for screen_name in screen_names:
        fetch_friends_for(screen_name, client, storage)


def fetch_followers_for(screen_name, client, storage):
    """
    Fetch followers for a twitter profile
    """

    followers_uri = twitter_uri('followers', 'ids')
    fetch_cursored_collection(client, screen_name, followers_uri,
        storage.store_followers)


def fetch_friends(client, screen_names, storage):
    """
    Fetch friends for all screen_names and store in storage_object
    """

    for screen_name in screen_names:
        fetch_friends_for(screen_name, client, storage)


def fetch_friends_for(screen_name, client, storage):
    """
    Fetch friends for a twitter profile
    """

    friends_uri = twitter_uri('friends', 'ids')
    fetch_cursored_collection(client, screen_name, friends_uri,
        storage.store_friends)


def fetch_cursored_collection(client, screen_name, resource_uri, storage_func):
    """
    Fetch each page of friends/followers collections for a screen name
    adding the resulting list by calling storage_func(screen_name, result)
    """

    cursor = -1
    result = []
    while True:
        response = client.get(resource_uri, params={'screen_name': screen_name,
            'cursor': cursor})
        if ok(response):
            result.extend(response.json['ids'])
            cursor = response.json['next_cursor']
            if cursor == 0:
                break
        elif rate_limited(response):
            client.wait_for(resource_uri)
        else:
            raise UnexpectedError(response.status_code, response.text)
        client.enhance_my_calm()
    storage_func(screen_name, result)


def ok(response):
    """
    Response is good
    """

    return response.status_code == 200


def rate_limited(response):
    """
    Response is rate limited"
    """

    return response.status_code == 429


if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: {} filename".format(sys.argv[0]))
        sys.exit(1)

    screen_names = source.load_source(filename)
    logger.info("starting with: {}".format(",".join(screen_names)))
    #storage = RedisStorage()
    storage = LoggingStorage()
    fetch(client, screen_names, storage)

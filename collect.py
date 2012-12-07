# encoding: utf-8
"""
Fetch twitter data for a SoMA panel from a source file of panelists
"""

from __future__ import unicode_literals, print_function

import sys
import multiprocessing
import logging
import time

import client
import data

logger = logging.getLogger('wood_panelling')


class UnexpectedError(Exception):
    """
    Well that was interesting…
    """


def fetch(client, screen_names, storage):
    """
    Set up and run separate processes for fetching each of:
    profiles, followers and friends adding them to the storage object
    """

    jobs = []
    args = (client, screen_names, storage)
    profiles = multiprocessing.Process(target=fetch_profiles, args=args)
    followers = multiprocessing.Process(target=fetch_followers, args=args)
    friends = multiprocessing.Process(target=fetch_friends, args=args)
    jobs = [
        profiles,
        followers,
        friends,
    ]
    logger.info("starting collection")
    [p.start() for p in jobs]
    [p.join() for p in jobs]
    logger.info("finished collection")


def fetch_profiles(client, screen_names, storage):
    """
    Fetch twitter profile information for screen_names and add them to storage

    Can request 100 profiles per request and 180 requests per 15mins
    """

    lookup_uri = client.twitter_uri('users', 'lookup')
    size_limit = 100

    while screen_names:
        clump = screen_names[:size_limit]
        response = client.get(lookup_uri,
            params={'screen_name': ",".join(clump)})
        if ok(response):
            del screen_names[:size_limit]
            for profile in response.json:
                storage.store_profile(profile)
            logger.debug("fetched {} profiles, {} left".format(len(clump),
                len(screen_names)))
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
        fetch_followers_for(screen_name, client, storage)


def fetch_followers_for(screen_name, client, storage):
    """
    Fetch followers for a twitter profile
    """

    followers_uri = client.twitter_uri('followers', 'ids', version='1')
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

    friends_uri = client.twitter_uri('friends', 'ids', version='1')
    fetch_cursored_collection(client, screen_name, friends_uri,
        storage.store_friends)


def fetch_cursored_collection(client, screen_name, resource_uri, storage_func):
    """
    Fetch each page of friends/followers collections for a screen name
    adding the resulting list by calling storage_func(screen_name, result)
    """

    cursor = -1
    result = []
    while cursor != 0:
        response = client.get(resource_uri, params={'screen_name': screen_name,
            'cursor': cursor})
        client.enhance_my_calm()
        if ok(response):
            logger.debug('fetched {} ids from {}'.format(
                len(response.json['ids']), resource_uri))
            result.extend(response.json['ids'])
            cursor = response.json['next_cursor']
            if cursor == 0:
                break
            logger.debug('next cursor {}'.format(cursor))
        elif not_found(response):
            pass
        elif rate_limited(response):
            client.wait_for(resource_uri)
        else:
            raise UnexpectedError(response.status_code, response.text)
    storage_func(screen_name, result)


def ok(response):
    """
    Response is good
    """

    return response.status_code == 200


def not_found(response):
    """
    Response wasn't found
    """

    return response.status_code in [404, 401]


def rate_limited(response):
    """
    Response is rate limited"
    """

    return response.status_code in [420, 429, 500, 502, 503, 504]


if __name__ == "__main__":
    handler = logging.FileHandler('fetch.log')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: {} filename".format(sys.argv[0]))
        sys.exit(1)

    screen_names = data.load_source(filename)
    logger.info("starting with: {}".format(",".join(screen_names)))
    fetch(client, screen_names, data.RedisStorage())
    handler.close()

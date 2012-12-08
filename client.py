"""
Connect to twitter
"""

from __future__ import unicode_literals, print_function

import time
import logging
import random
from functools import partial
from urlparse import urlparse
from os.path import splitext
import requests
from requests.auth import OAuth1

import config


requests.defaults.defaults['max_retries'] = 2

logger = logging.getLogger('wood_panelling')

auth = OAuth1(client_key=config.twitter('consumer_key'),
    client_secret=config.twitter('consumer_secret'),
    resource_owner_key=config.twitter('access_token'),
    resource_owner_secret=config.twitter('access_token_secret'),
    signature_type='query')

get = partial(requests.get, auth=auth)
post = partial(requests.post, auth=auth)


def twitter_uri(group, method, version='1.1'):
    """
    Get full uri for api endpoint
    """

    return "https://api.twitter.com/{}/{}/{}.json".format(
        version, group, method)


def wait_time(resource_uri):
    """
    Find out how long we need to wait before accessing a certain api endpoint
    """

    ratelimit_uri = twitter_uri('application', 'rate_limit_status')
    group, method = splitext(urlparse(resource_uri).path)[0].split('/')[-2:]
    info = get(ratelimit_uri, params={'resources': group})
    endpoint = "/{}/{}".format(group, method)
    try:
        timestamp = info.json['resources'][group][endpoint]['reset']
        # add 1 second to account for fractions of a
        # second which are not returned in timestamp
        return timestamp - int(time.time()) + 1
    except KeyError:
        return 60


def wait_for(resource_uri):
    """
    Wait for long enough so we can access this api endpoint again
    """

    delay = wait_time(resource_uri)
    logger.info("rate limit for {} (delay: {})".format(resource_uri, delay))
    time.sleep(delay)
    pause = random.uniform(60, 300)
    logger.info("waiting for an extra {} seconds".format(pause))
    time.sleep(pause)


def enhance_my_calm():
    """
    Wait a little bit to not hammer twitter i.e. reduce the chance of being
    banned as a robot
    """

    pause = random.random() / 4
    logger.info("calming for {} seconds".format(pause))
    time.sleep(pause)

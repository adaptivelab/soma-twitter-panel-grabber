"""
Connect to twitter
"""

from __future__ import unicode_literals, print_function

import ConfigParser as configparser
import time
import logging
import random
from functools import partial
from urlparse import urlparse
from os.path import splitext
import requests
from requests.auth import OAuth1


logger = logging.getLogger('wood_panelling')

config = configparser.ConfigParser()
config.read('config.ini')
twitter_config = partial(config.get, 'twitter')
auth = OAuth1(client_key=twitter_config('consumer_key'),
    client_secret=twitter_config('consumer_secret'),
    resource_owner_key=twitter_config('access_token'),
    resource_owner_secret=twitter_config('access_token_secret'),
    signature_type='query')

get = partial(requests.get, auth=auth)
post = partial(requests.post, auth=auth)


def wait_time(resource_uri):
    """
    Find out how long we need to wait before accessing a certain api endpoint
    """

    ratelimit_uri = "https://api.twitter.com/1.1/application/rate_limit_status"
    group, method = splitext(urlparse(resource_uri).path)[0].split('/')[-2:]
    info = get(ratelimit_uri, params={'resources': group})
    endpoint = "/%s/%s" % (group, method)
    timestamp = info.json['resources'][group][endpoint]['reset']
    # add 1 second to account for fractions of a
    # second which are not returned in timestamp
    return timestamp - int(time.time()) + 1


def wait_for(resource_uri):
    """
    Wait for long enough so we can access this api endpoint again
    """

    delay = wait_time(resource_uri)
    logger.info("rate limit for {} (delay: {})".format(resource_uri, delay))
    time.sleep(delay)


def enhance_my_calm():
    """
    Wait a little bit to not hammer twitter i.e. reduce the chance of being
    banned as a robot
    """

    time.sleep(random.uniform(1, 5))

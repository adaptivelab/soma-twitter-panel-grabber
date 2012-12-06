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


logger = logging.getLogger('wood_panelling')

# twitter oauth details
CONSUMER_KEY = "client key"
CONSUMER_SECRET = "client secret"
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
ACCESS_TOKEN = "user token"
ACCESS_TOKEN_SECRET = "user secret"

auth = OAuth1(client_key=CONSUMER_KEY, client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN, resource_owner_secret=ACCESS_TOKEN_SECRET,
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

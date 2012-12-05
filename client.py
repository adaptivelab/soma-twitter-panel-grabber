"""
Connect to twitter
"""

from __future__ import unicode_literals, print_function

from functools import partial
import requests
from requests.auth import OAuth1


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

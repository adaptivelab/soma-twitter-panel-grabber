"""
Connect to twitter
"""

from __future__ import unicode_literals, print_function

import oauth2 as oauth


# twitter oauth details 
CONSUMER_KEY = "client key"
CONSUMER_SECRET = "client secret"
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
ACCESS_TOKEN = "user token"
ACCESS_TOKEN_SECRET = "user secret"

def client():
    """
    Create an oauth client object to access resources
    """

    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    access_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_TOKEN_SECRET)
    return oauth.Client(consumer, access_token)

from __future__ import unicode_literals, print_function

import time
from flexmock import flexmock
from nose.tools import *

import collect


def test_collection_of_profile_information():
    user_lookup = [
        {'id': '1234', 'screen_name': 'alice'},
        {'id': '4321', 'screen_name': 'bob'}
    ]
    client = flexmock()
    client.should_receive('get').and_return(flexmock(status_code=200, json=user_lookup))
    storage = flexmock()
    for profile in user_lookup:
        storage.should_receive('store_profile').with_args(profile).once()
    collect.fetch_profiles(client, ['alice', 'bob'], storage)


def test_sleep_until_reset_calculation_adds_one_second():
    reset_time = int(time.time()) + 4*60
    info = {
        'resources': {
            'users': {
                '/users/lookup': { 'reset': reset_time }
            }
        }
    }
    client = flexmock()
    client.should_receive('get').and_return(flexmock(status_code=200, json=info))
    assert_equal(4*60 + 1, collect.wait_time(client, 'https://api.twiter.com/1.1/users/lookup.json'))

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
    client.should_receive('get').and_return(
        flexmock(status_code=200, json=user_lookup))
    storage = flexmock()
    for profile in user_lookup:
        storage.should_receive('store_profile').with_args(profile).once()
    collect.fetch_profiles(client, ['alice', 'bob'], storage)


def test_sleep_until_reset_calculation_adds_one_second():
    reset_time = int(time.time()) + (4 * 60)
    info = {
        'resources': {
            'users': {
                '/users/lookup': {'reset': reset_time}
            }
        }
    }
    client = flexmock()
    client.should_receive('get').and_return(
        flexmock(status_code=200, json=info))
    assert_equal((4 * 60) + 1,
        collect.wait_time(client,
            'https://api.twiter.com/1.1/users/lookup.json'))


def test_429_response_causes_a_wait():
    reset_time = int(time.time()) + 10
    rate_info = {
        'resources': {
            'users': {
                '/users/lookup': {'reset': reset_time}
            }
        }
    }
    user_info = [{'id': '1234', 'screen_name': 'test'}]

    client = flexmock()
    storage = flexmock()
    storage.should_receive('store_profile').with_args(user_info[0])

    client.should_receive('get').and_return(
        flexmock(status_code=429)
    ).and_return(
        flexmock(status_code=200, json=rate_info)
    ).and_return(
        flexmock(status_code=200, json=user_info)
    )
    # one extra second than reset time
    flexmock(time).should_receive('sleep').with_args(11)
    collect.fetch_profiles(client, ['test'], storage)


def test_fetching_followers_paginates():
    followers = range(100)
    screen_name = 'test_user'
    client = flexmock()
    storage = flexmock()
    first_set = {'ids': followers[:50], 'next_cursor': 50}
    second_set = {'ids': followers[50:], 'next_cursor': 0}

    client.should_receive('get').and_return(
        flexmock(status_code=200, json=first_set)
    ).and_return(
        flexmock(status_code=200, json=second_set)
    )
    storage.should_receive('store_followers').with_args(screen_name, followers)
    collect.fetch_followers_for(screen_name, client, storage)


def test_fetching_friends_paginates():
    friends = range(100)
    screen_name = 'test_user'
    client = flexmock()
    storage = flexmock()
    first_set = {'ids': friends[:50], 'next_cursor': 50}
    second_set = {'ids': friends[50:], 'next_cursor': 0}

    client.should_receive('get').and_return(
        flexmock(status_code=200, json=first_set)
    ).and_return(
        flexmock(status_code=200, json=second_set)
    )
    storage.should_receive('store_friends').with_args(screen_name, friends)
    collect.fetch_friends_for(screen_name, client, storage)

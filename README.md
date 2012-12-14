Twitter panel data collection
=============================

A tool for fetching twitter profile, follower and friend info for SoMA

currently requires a redis database to write it's intermediate results too

Installation
------------

    virtualenv env
    . env/bin/activate
    pip install -r requirements.txt

    # install redis
    apt-get install redis-server
    # or
    brew install redis

Setup
-----

It needs a config.ini file (look at config.ini.example) to give it a twitter api account
and to tell it which redis server/database to connect to

    [twitter]
    consumer_key = client key value
    consumer_secret = client secret value
    access_token = token
    access_token_secret = token secret

    [redis]
    host = localhost
    port = 6379
    db = 0

Running
-------

collect.py will take a newline separated list of twitter names and collect profile,
followers and friend ids, it will take a while unless you have a less rate limited
twitter account

    python collect.py list-of-twitter-names.txt

Outputing results
-----------------

output.py will write out lines of json represening the panelist info for SoMA and
also write out a list of twitter names where it couldn't collect some of the data
it needs a mapping of twitter screen names to yougov panelist ids (a previous
panel_default.json will suffice or a csv of [screen_name, id] rows)

    python output.py panel.json mapping_for_yougov_id.[csv,json] missing-names.txt

This uses the panoptic proxy provided by beta.pulse.yougov.com, access to the us panoptic
is trickier at the moment.

open an ssh connection to the alab-pulse1 machine and set up a socks proxy to port 8050

    # connect to yougov vpn and then set up this proxy
    ssh -ND 8050 username@alab-pulse1
    # in another terminal
    python us_output.py us_panel.json mapping_for_yougov_id.csv missing-us-names.txt

# encoding: utf-8
"""
Update a SoMA panel from collected twitter data
"""

from __future__ import unicode_literals, print_function

import sys
import csv
import json

import data


class YouGovIDMapJSON(dict):

    def __init__(self, filename):
        with open(filename) as f:
            data = [json.loads(line) for line in f]
        for record in data:
            yougov_id = record['yougov']['id']
            screen_name = record['twitter']['screen_name']
            self[screen_name.lower()] = yougov_id


class YouGovIDMapCSV(dict):

    def __init__(self, filename):
        with open(filename) as f:
            for screen_name, id in csv.reader(f):
                if screen_name.lower() == 'n/a':
                    continue
                screen_name = screen_name.replace('@', '').replace('/', '')
                self[screen_name.lower()] = id


def yougov_idmap(filename):
    if filename.endswith('.csv'):
        return YouGovIDMapCSV(filename)
    elif filename.endswith('.json'):
        return YouGovIDMapJSON(filename)
    return {}


def panelist_info(rs, screen_name, idmap, missing_info):
    """
    Collect the panelist info from redis
    adding screen_name to a missing set if there is a keyerror
    """

    try:
        info = rs.panelist_info(screen_name)
        if screen_name.lower() in idmap:
            info['yougov'] = {'id': idmap[screen_name.lower()]}
        return json.dumps(info)
    except KeyError:
        missing_info.add(screen_name)


def export_to_json(filename, idmap, missing):
    """
    Write out everything as json to filename
    missing screen_names to missing
    """

    rs = data.RedisSource()
    missing_info = set()
    with open(filename, 'w') as io:
        for screen_name in rs.screen_names:
            info = panelist_info(rs, screen_name, idmap, missing_info)
            if info:
                io.write(info)
                io.write("\n")
    if missing_info:
        print("missing info for {}".format(len(missing_info)))
        with open(missing, 'w') as io:
            io.write("\n".join(missing_info))


if __name__ == "__main__":
    try:
        filename, idmapname, missingname = sys.argv[1:]
    except KeyError:
        print("Usage: {} filename yougovid.[json,csv] missingname".format(sys.argv[0]))
        sys.exit(1)

    export_to_json(filename, yougov_idmap(idmapname), missingname)

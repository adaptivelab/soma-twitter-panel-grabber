# encoding: utf-8
"""
Update a SoMA panel from collected twitter data
"""

from __future__ import unicode_literals, print_function

import sys
import csv
import json

import data
from output import yougov_idmap


def panelist_info(rs, screen_name, idmap, missing_info):
    """
    Collect the panelist info from redis
    adding screen_name to a missing set if there is a keyerror
    """

    try:
        info = rs.panelist_info(screen_name)
        if screen_name.lower() in idmap:
            yougov_id = idmap[screen_name.lower()]
            info['yougov'] = {'id': yougov_id}
            panoptic = data.us_panoptic_data(yougov_id)
            if panoptic:
                info['panoptic'] = panoptic
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
        print("Usage: {} filename yougovid.[json,csv] missingname".format(
            sys.argv[0]))
        sys.exit(1)

    export_to_json(filename, yougov_idmap(idmapname), missingname)

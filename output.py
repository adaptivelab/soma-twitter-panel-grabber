# encoding: utf-8
"""
Update a SoMA panel from collected twitter data
"""

from __future__ import unicode_literals, print_function

import sys
import json

import data


def panelist_info(rs, screen_name, missing_info):
    """
    Collect the panelist info from redis
    adding screen_name to a missing set if there is a keyerror
    """

    try:
        info = rs.panelist_info(screen_name)
        return json.dumps(info)
    except KeyError:
        missing_info.add(screen_name)


def export_to_json(filename, missing):
    """
    Write out everything as json to filename
    missing screen_names to missing
    """

    rs = data.RedisSource()
    missing_info = set()
    with open(filename, 'w') as io:
        for screen_name in rs.screen_names:
            info = panelist_info(rs, screen_name, missing_info)
            if info:
                io.write(info)
                io.write("\n")
    if missing_info:
        print("missing info for {}".format(len(missing_info)))
        with open(missing, 'w') as io:
            io.write("\n".join(missing_info))


if __name__ == "__main__":
    try:
        filename, missingname = sys.argv[1:3]
    except KeyError:
        print("Usage: {} filename missingname".format(sys.argv[0]))
        sys.exit(1)

    export_to_json(filename, missingname)

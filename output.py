# encoding: utf-8
"""
Update a SoMA panel from collected twitter data
"""

from __future__ import unicode_literals, print_function

import sys
import json

import data


def panelist_info(rs):
    """
    Collect the panelist info from redis
    adding screen_name to a missing set if there is a keyerror
    """

    missing_info = set()
    data = []
    for screen_name in rs.screen_names:
        try:
            info = rs.panelist_info(screen_name)
            data.append(info)
        except KeyError:
            missing_info.add(screen_name)
    return data, missing_info


def export_to_json(filename, missing):
    """
    Write out everything as json to filename
    missing screen_names to missing
    """

    rs = data.RedisSource()
    panelists, missing_info = panelist_info(rs)
    with open(filename, 'w') as io:
        io.write(json.dumps(panelists, indent=2))
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

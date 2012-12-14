"""
Put the panel data into couchdb from redis
"""

import couchdb

import data


def export_to_couch(rs, db):
    for screen_name in rs.screen_names:
        try:
            info = rs.panelist_info(screen_name)
            db.save(info)
        except KeyError:
            pass


if __name__ == "__main__":
    rs = data.RedisSource()
    couch = couchdb.Server()
    db_name = 'soma-panel-uk'
    db = couch[db_name] if db_name in couch else couch.create(db_name)
    export_to_couch(rs, db)

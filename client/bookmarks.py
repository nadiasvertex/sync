import os
from datetime import datetime
import requests
import sqlite3

__author__ = 'Christopher Nelson'

import json
from pprint import pprint
from urlparse import urlparse, urlunparse

bookmark_db = "bookmarks.db"
bookmark_schema = \
    """
    CREATE TABLE bookmark(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pub VARCHAR UNIQUE,
        version INTEGER,
        dirty BOOL,
        data VARCHAR
    );
    """


def ensure_db():
    if not os.path.exists(bookmark_db):
        db = sqlite3.connect(bookmark_db)
        db.execute(bookmark_schema)
        db.commit()
        db.close()


def load_bookmarks(pub):
    ensure_db()
    con = sqlite3.connect(bookmark_db)
    con.row_factory = sqlite3.Row
    try:
        for row in con.execute("SELECT * FROM bookmark WHERE pub=?", (pub,)):
            return {
                "version": row["version"],
                "dirty": row["dirty"],
                "bookmarks": json.loads(row["data"])
            }
    finally:
        con.close()

    return None


def store_bookmarks(pub, data):
    ensure_db()
    con = sqlite3.connect(bookmark_db)
    with con:
        con.execute(
            "REPLACE INTO bookmark(pub, version, dirty, data) VALUES(?, ?, ?, ?)",
            (pub, data["version"], data["dirty"], json.dumps(data["bookmarks"]))
        )

    con.close()


def load():
    ensure_db()
    with open(bookmark_db) as i:
        return json.load(i)


def store(db):
    with open(bookmark_db, "w") as o:
        json.dump(db, o)


def sync_bookmarks(url, pub):
    ensure_db()
    pub_db = load_bookmarks(pub)
    p_url = urlparse(url)
    r_url = urlunparse((p_url[0], p_url[1], "/bookmark/1/%s" % pub, None, None, None))
    r = requests.put(r_url, json.dumps(pub_db["bookmarks"]).encode("utf-8")).json()
    pprint(r)
    if r["error"]:
        print("Failed to synchronize '%s' bookmarks:\n%s" % (pub, r["message"]))
        return
    else:
        results = r["value"]
        store_bookmarks(
            pub,
            {"version": results["version"],
             "dirty": False,
             "bookmarks": results["data"]}
        )


def get_bookmark_status(url, local=True):
    p_url = urlparse(url)
    r_url = urlunparse((p_url[0], p_url[1], "/bookmarks/1/", None, None, None))
    return requests.get(r_url).json()


def get_bookmarks(pub):
    pub_db = load_bookmarks(pub)
    if pub_db is not None:
        pprint(pub_db)
    else:
        print("-empty-")


def set_bookmark(pub, slot, citation):
    pub_db = load_bookmarks(pub)
    if pub_db is None:
        pub_db = {"version": -1, "dirty": True, "bookmarks": {}}
    slot_entry = pub_db["bookmarks"].setdefault(slot, {})
    slot_entry["when"] = datetime.now().isoformat()
    slot_entry["value"] = "ref://" + citation
    store_bookmarks(pub, pub_db)


def del_bookmark(pub, slot):
    pub_db = load_bookmarks(pub)
    if pub_db is not None and slot in pub_db["bookmarks"]:
        pub_db["dirty"] = True
        slot_entry = pub_db["bookmarks"].get(slot)
        slot_entry["when"] = datetime.now().isoformat()
        slot_entry["value"] = None
        store_bookmarks(pub, pub_db)

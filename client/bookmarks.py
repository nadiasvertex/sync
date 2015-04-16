import os
from datetime import datetime
import requests
import sqlite3
import sys

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


def load_bookmarks_status():
    ensure_db()
    con = sqlite3.connect(bookmark_db)
    con.row_factory = sqlite3.Row
    try:
        return [
            {
                "version": row["version"],
                "dirty": row["dirty"],
                "pub": row["pub"]
            } for row in con.execute("SELECT pub, version, dirty FROM bookmark")]
    finally:
        con.close()


def store_bookmarks(pub, data):
    ensure_db()
    con = sqlite3.connect(bookmark_db)
    with con:
        con.execute(
            "REPLACE INTO bookmark(pub, version, dirty, data) VALUES(?, ?, ?, ?)",
            (pub, data["version"], data["dirty"], json.dumps(data["bookmarks"]))
        )

    con.close()


def sync_bookmarks(url, pub):
    ensure_db()
    pub_db = load_bookmarks(pub)
    p_url = urlparse(url)
    r_url = urlunparse((p_url[0], p_url[1], "/bookmark/1/%s" % pub, None, None, None))
    r = requests.put(r_url, json.dumps(pub_db["bookmarks"]).encode("utf-8")).json()
    pprint(r)
    if r["error"]:
        print("Failed to synchronize '%s' bookmarks:\n%s" % (pub, r["error-message"]))
        return
    else:
        results = r["value"]
        store_bookmarks(
            pub,
            {"version": results["version"],
             "dirty": False,
             "bookmarks": results["data"]}
        )


def sync_all_bookmarks(url):
    r_status = get_bookmark_status(url, local=False)
    l_status = get_bookmark_status(url)
    # pprint(r_status)
    #pprint(l_status)
    if r_status["error"]:
        print("Failed to request bookmark status.")
        sys.exit(1)
    else:
        r_status = r_status["value"]

    r_index = {i["pub"]: i for i in r_status}
    l_index = {i["pub"]: i for i in l_status}

    pubs = sorted(set(r_index.keys()).union(set(l_index.keys())))
    for item in pubs:
        r_item = r_index.get(item)
        l_item = l_index.get(item)
        needs_update = \
            item not in l_index or \
            item not in r_index or \
            l_item.get("dirty", False) or \
            l_item.get("version", -1) < r_item.get("version")

        print("%s %s local=%s remote=%s" % (
            "*" if needs_update else " ",
            item,
            "not present" if l_item is None else l_item.get("version"),
            "not present" if r_item is None else r_item.get("version")
        ))
        if needs_update:
            sync_bookmarks(url, item)


def get_bookmark_status(url, local=True):
    if not local:
        p_url = urlparse(url)
        r_url = urlunparse((p_url[0], p_url[1], "/bookmarks/1/", None, None, None))
        return requests.get(r_url).json()
    else:
        return load_bookmarks_status()


def get_bookmarks(pub):
    pub_db = load_bookmarks(pub)
    if pub_db is not None:
        pprint(pub_db)
    else:
        print("-empty-")


def set_bookmark(pub, slot, citation):
    pub_db = load_bookmarks(pub)
    if pub_db is None:
        pub_db = {"version": -1, "dirty": False, "bookmarks": {}}

    pub_db["dirty"] = True
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

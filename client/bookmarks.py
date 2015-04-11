import os
from datetime import datetime
import requests

__author__ = 'Christopher Nelson'

import json
from pprint import pprint
from urlparse import urlparse, urlunparse

bookmark_db = "bookmarks.json"

def ensure_db():
    if not os.path.exists(bookmark_db):
        with open(bookmark_db, "w") as o:
            o.write("{}")

def load():
    ensure_db()
    with open(bookmark_db) as i:
        return json.load(i)

def store(db):
    with open(bookmark_db, "w") as o:
        json.dump(db, o)

def sync_bookmarks(url, pub):
    ensure_db()
    db = load()
    pub_db = db.get(pub)
    p_url = urlparse(url)
    r_url = urlunparse((p_url[0], p_url[1], "/bookmark/1/%s" % pub, None, None, None))
    db[pub] = requests.put(r_url, json.dumps(pub_db).encode("utf-8")).json()
    store()

def get_bookmarks(pub):
    db = load()
    pub_db = db.get(pub)
    if pub_db is not None:
        pprint(pub_db)
    else:
        print("-empty-")

def set_bookmark(pub, slot, citation):
    db = load()
    pub_db = db.setdefault(pub, {})
    slot_entry = pub_db.setdefault(slot, {})
    slot_entry["when"] = datetime.now().isoformat()
    slot_entry["value"] = "ref://" + citation
    store(db)

def del_bookmark(pub, slot):
    db = load()
    pub_db = db.get(pub)
    if pub_db is not None and slot in pub_db:
        slot_entry = pub_db.get(slot)
        slot_entry["when"] = datetime.now().isoformat()
        slot_entry["value"] = None
        store(db)

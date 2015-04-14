import os

__author__ = 'Christopher Nelson'

import json

annotation_db = "annotations.json"


def ensure_db():
    if not os.path.exists(annotation_db):
        with open(annotation_db, "w") as o:
            o.write("{}")


def load():
    ensure_db()
    with open(annotation_db) as i:
        return json.load(i)


def store(db):
    with open(annotation_db, "w") as o:
        json.dump(db, o)


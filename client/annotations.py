from datetime import datetime
import json
import os
from pprint import pprint
import requests
import sqlite3
from urlparse import urlparse, urlunparse
import uuid

__author__ = 'Christopher Nelson'

annotation_db = "annotations.db"
annotation_schema = \
    """
    CREATE TABLE annotation(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pub VARCHAR,
        citation VARCHAR,
        version INTEGER,
        dirty BOOL,
        CONSTRAINT annotation_unique UNIQUE (pub, citation)
    );

    CREATE TABLE highlight(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        annotation_id INTEGER,
        note_id INTEGER,
        uuid VARCHAR UNIQUE,
        range VARCHAR,
        ts VARCHAR
    );

    CREATE TABLE note(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        annotation_id INTEGER,
        uuid VARCHAR UNIQUE,
        text VARCHAR,
        ts VARCHAR
    );
    """


def ensure_db():
    if not os.path.exists(annotation_db):
        db = sqlite3.connect(annotation_db)
        db.executescript(annotation_schema)
        db.commit()
        db.close()


def store_annotations(pub, citation, data):
    """
    Store annotation data under the given pub/citation.

    :param pub: The publication to select.
    :param citation: The citation to select.
    :param data: The data to store.
    """
    ensure_db()
    con = sqlite3.connect(annotation_db)
    with con:
        cur = con.cursor()
        cur.execute(
            "REPLACE INTO annotation(pub, citation, version, dirty) VALUES(?, ?, ?, ?)",
            (pub, citation, data["version"], data["dirty"])
        )
        cur.execute("SELECT id FROM annotation WHERE pub=? AND citation=?", (pub,citation))
        annotation_id = cur.fetchone()[0]

        for k, v in data["notes"].items():
            cur.execute(
                "REPLACE INTO note(annotation_id, uuid, text, ts) VALUES(?,?,?,?)",
                (annotation_id, k, v["text"], v["when"])
            )

        for k, v in data["highlights"].items():
            note_id = v["note-id"]
            if note_id is not None:
                note_id = note_id
                cur.execute("SELECT id FROM note WHERE uuid=?", (note_id, ))
                r = cur.fetchone()
                pprint(r)
                if r is None:
                    pprint("Data inconsistent: no such note: '%s'" % note_id)
                    note_id = None
                else:
                    note_id = r[0]

            pprint((annotation_id, note_id, k, v["range"], v["when"]))

            cur.execute(
                "REPLACE INTO highlight(annotation_id, note_id, uuid, range, ts) VALUES(?,?,?,?,?)",
                (annotation_id, note_id, k, v["range"], v["when"])
            )

    con.close()


def load_annotations(pub, citation):
    ensure_db()
    con = sqlite3.connect(annotation_db)
    con.row_factory = sqlite3.Row
    data = {}
    cur = con.cursor()
    cur.execute("SELECT id, version, dirty FROM annotation WHERE pub=? AND citation=?", (pub, citation))
    v = cur.fetchone()
    if v is None:
        return None

    annotation_id = v["id"]
    data["version"] = v["version"]
    data["dirty"] = v["dirty"]
    highlights = {}
    notes = {}

    for r in cur.execute("SELECT * FROM note WHERE annotation_id=?", (annotation_id,)):
        notes[r["uuid"]] = {"text": r["text"], "when": r["ts"]}

    for r in cur.execute("SELECT h.uuid AS uuid, n.id AS note_id, h.range AS range, h.ts AS ts "
                         "FROM highlight AS h "
                         "LEFT OUTER JOIN note AS n ON h.note_id=n.id "
                         "WHERE h.annotation_id=?", (annotation_id,)):
        highlights[r["uuid"]] = {"range": r["range"], "when": r["ts"], "note-id": r["note_id"]}

    data["highlights"] = highlights
    data["notes"] = notes
    con.close()

    return data


def get_annotations(pub, citation):
    a = load_annotations(pub, citation)
    if a:
        pprint(a)
    else:
        print("-empty-")


def add_highlight(pub, citation, text_range, note):
    a = load_annotations(pub, citation)
    if a is None:
        a = {"highlights": {}, "notes": {}, "version": -1, "dirty": False}
    h_id = str(uuid.uuid4())
    h = a["highlights"].setdefault(h_id, {})
    h["range"] = text_range
    h["when"] = datetime.now().isoformat()

    if note is not None:
        n = a["notes"]
        n_id = str(uuid.uuid4())
        n[n_id] = {"text": note, "when": h["when"]}
        h["note-id"] = n_id
    else:
        h["note-id"] = None

    a["dirty"] = True
    store_annotations(pub, citation, a)


def add_note(pub, citation, note):
    a = load_annotations(pub, citation)
    if a is None:
        a = {"highlights": {}, "notes": {}, "version": -1, "dirty": False}

    n = a["notes"]
    n_id = str(uuid.uuid4())
    n[n_id] = {"text": note, "when": datetime.now().isoformat()}

    a["dirty"] = True
    store_annotations(pub, citation, a)


def sync_annotations(url, pub, citation):
    a = load_annotations(pub, citation)
    p_url = urlparse(url)
    r_url = urlunparse((p_url[0], p_url[1], "/annotation/1/%s" % pub, None, None, None))
    r = requests.put(r_url, json.dumps(a).encode("utf-8")).json()
    pprint(r)
    if r["error"]:
        print("Failed to synchronize '%s/%s' annotations:\n%s" % (pub, citation, r["message"]))
        return
    else:
        results = r["value"]
        data = results["data"]
        store_annotations(
            pub,
            citation,
            {"version": results["version"],
             "dirty": False,
             "highlights": data["highlights"],
             "notes": data["notes"]}
        )

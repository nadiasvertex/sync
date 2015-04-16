import json
from pprint import pprint
import traceback

from elasticsearch import Elasticsearch

import uwsgi
import store_zk
import bookmark_mgr
import annotation_mgr


_ = uwsgi

# ZooKeeper hosts
zk_hosts = [
    "192.168.33.10",
    "192.168.33.11",
    "192.168.33.12"
]


def bookmark_handler(env, elements):
    st = store_zk.Store(zk_hosts)
    bookmarks = bookmark_mgr.Bookmarks(st)

    print("processing bookmark request: %s" % str(elements))
    uid = elements[0]
    pub = elements[1]

    method = env["REQUEST_METHOD"]
    with st:
        if method == "GET":
            return bookmarks.get(uid, pub)
        elif method == "PUT":
            bookmark_data = json.loads(env['wsgi.input'].read())
            return bookmarks.update(uid, pub, bookmark_data)


def bookmark_collection_handler(env, elements):
    st = store_zk.Store(zk_hosts)
    bookmarks = bookmark_mgr.Bookmarks(st)

    print("processing bookmark collection request: %s" % str(elements))
    uid = elements[0]

    method = env["REQUEST_METHOD"]
    with st:
        if method == "GET":
            return bookmarks.get_status(uid)


def annotation_handler(env, elements):
    st = store_zk.Store(zk_hosts)
    es = Elasticsearch(zk_hosts, sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
    annotations = annotation_mgr.Annotations(st, es)

    print("processing annotation request: %s" % str(elements))
    uid = elements[0]
    pub = elements[1]
    citation = "%s/%s" % (elements[2], elements[3])

    method = env["REQUEST_METHOD"]
    with st:
        if method == "GET":
            return annotations.get(uid, pub, citation)
        elif method == "POST":
            annotation_data = json.loads(env['wsgi.input'].read())
            if "highlight" in annotation_data:
                return annotations.add_highlight(
                    uid, pub, citation,
                    annotation_data.get("highlight"),
                    annotation_data.get("note")
                )
            elif "note" in annotation_data:
                return annotations.add_note(
                    uid, pub, citation,
                    annotation_data.get("note")
                )
            else:
                raise ValueError("Require 'highlight' or 'note' (or both) for this request.")
        elif method == "PUT":
            annotation_data = json.loads(env['wsgi.input'].read())
            return annotations.update(uid, pub, citation, annotation_data)

def annotation_collection_handler(env, elements):
    st = store_zk.Store(zk_hosts)
    es = Elasticsearch(zk_hosts, sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
    annotations = annotation_mgr.Annotations(st, es)

    print("processing annotation collection request: %s" % str(elements))
    uid = elements[0]

    method = env["REQUEST_METHOD"]
    with st:
        if method == "GET":
            return annotations.get_status(uid)

def search_handler(env, elements):
    st = store_zk.Store(zk_hosts)
    es = Elasticsearch(zk_hosts, sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
    annotations = annotation_mgr.Annotations(st, es)

    uid = elements[0]
    term = env["QUERY_STRING"].split("=")[1]

    print("processing search request: %s (term=%s)" % (str(elements), term))

    method = env["REQUEST_METHOD"]
    with st:
        if method == "GET":
            return annotations.search(uid, term)


handlers = {
    "bookmark": bookmark_handler,
    "bookmarks": bookmark_collection_handler,
    "annotation": annotation_handler,
    "annotations": annotation_collection_handler,
    "search": search_handler
}


def application(env, start_response):
    print(env)

    parts = env["REQUEST_URI"].split("/")
    print(parts)
    handler = handlers.get(parts[1])
    if handler is None:
        start_response('400 Bad Request', [('Content-Type', 'text/json')])
        return [json.dumps(
            {"error": True,
             "error-message": "Unknown request: '%s'" % parts[1]
            }).encode("utf-8")
        ]

    try:
        r = handler(env, parts[2:])
        start_response('200 OK', [('Content-Type', 'text/json')])
        return [json.dumps({"error": False, "value": r}).encode("utf-8")]

    except:
        start_response('500 Internal Server Error', [('Content-Type', 'text/json')])
        return [json.dumps(
            {
                "error": True,
                "error-message": traceback.format_exc()
            }).encode("utf-8")
        ]

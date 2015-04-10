import json
import traceback

import uwsgi
import store_cb
import bookmark_mgr


_ = uwsgi

# Couchbase hosts
cb_hosts = [
    "192.168.33.10",
    "192.168.33.11",
    "192.168.33.12"
]


def bookmark_handler(env, elements):
    st = store_cb.Store(cb_hosts)
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


handlers = {
    "bookmark": bookmark_handler
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

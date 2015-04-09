import json
import traceback

import store_zk
import bookmark_mgr


# Simple store (not distributed, not safe. For local testing only.)
# st = store.Store()

# ZooKeeper store.
st = store_zk.Store(
    [
        "192.168.33.10",
        "192.168.33.11"
        "192.168.33.12"
    ]
)

bookmarks = bookmark_mgr.Bookmarks(st)


def bookmark_handler(env, elements):
    if env["REQUEST_METHOD"] == "GET":
        return bookmarks.get(elements[0], elements[1])
    elif env["REQUEST_METHOD"] == "PUT":
        return bookmarks.update(elements[0], elements[1])

handlers = {
    "bookmark": bookmark_handler
}


def application(env, start_response):
    print(env)

    parts = env["REQUEST_URI"].split("/")
    handler = handlers.get(parts[0])
    if handler is None:
        start_response('400 Bad Request', [('Content-Type', 'text/json')])
        return [json.dumps(
            {"error": True,
             "error-message": "Unknown request '%s'" % parts[0]
            }).encode("utf-8")
        ]

    try:
        r = handler(env, parts[1:])
        start_response('200 OK', [('Content-Type', 'text/json')])
        return [json.dumps({"error" : False, "value" : r}).encode("utf-8")]

    except:
        start_response('500 Internal Server Error', [('Content-Type', 'text/json')])
        return [json.dumps(
            {
                "error": True,
                "error-message": traceback.format_exc()
            }).encode("utf-8")
        ]

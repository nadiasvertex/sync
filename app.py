import uwsgi
import store
import bookmark_mgr

def application(env, start_response):
    print(env)
    start_response('200 OK', [('Content-Type', 'text/json')])
    return [b'{"hello":"world"}']


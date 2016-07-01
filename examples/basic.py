#!/usr/bin/env python3

# ab -n 1000 -c 10 http://localhost:8080/hello/world
# ab -n 2 -c 2 http://127.0.0.1:8080/hello/world

import gevent.monkey
gevent.monkey.patch_all()

import sys
sys.path.insert(0, '..')
import plus
import time
import bottle

app = bottle.Bottle()
app.config.load_config('basic.config')
app.install(plus.Canister())

@app.get('/')
def index(foo=None):
    req = bottle.request
    session = req.session
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 0
        
    # Logging something
    app.log.info('Hey!')
    app.log.warning('Ho!')
    
    res = '<pre>'
    res += 'Foo: %s\n' % foo
    res += 'Session id: %s\n' % req.session_id
    res += 'Counter: %s\n' % session['counter']
    res += 'User: %s\n' % req.user
    res += '</pre>'
    res += '<a href="secret">Basic Auth</a> (username: alice, password: my-secret)</a>'

    return res
    
@app.get('/secret')
def secret():
    req = bottle.request
    
    if not req.user:
        err = bottle.HTTPError(401, "Login required")
        err.add_header('WWW-Authenticate', 'Basic realm="%s"' % 'private')
        return err

    return 'You are authenticated as ' + str(req.user)

app.run(host='0.0.0.0', server='gevent', log=app.log, error_log=app.log, debug=True)
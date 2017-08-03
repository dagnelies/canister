#!/usr/bin/env python3

# ab -n 1000 -c 10 http://localhost:8080/hello/world
# ab -n 2 -c 2 http://127.0.0.1:8080/hello/world

import sys
sys.path.insert(0, '..')
import canister
import time
import bottle
from canister import session

app = bottle.Bottle()
app.config.load_config('7_oauth2.config')
app.install(canister.Canister())

@app.get('/')
def index():
    return '''
        <pre>
            Session sid: %s
            Session user: %s
        </pre>
        Now try to send a brearer token in the Authorization header. 
    ''' % (session.sid, session.user)

app.run(host='0.0.0.0')
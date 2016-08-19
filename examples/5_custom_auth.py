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
app.install(canister.Canister())

@app.get('/')
def index():
    return '''
        <pre>
            Session sid: %s
            Session user: %s
        </pre>
        <form target="/login">
        <a href="/login?username">My private area</a> (username: alice, password: my-secret)</a>
    ''' % (session.sid, session.user)

    
@app.get('/login')
def login(username, password):
    session.user = username
    return 'Welcome %s! <a href="/">Go back</a> <a href="/logout">Log out</a>' % session.user

@app.get('/logout')
def logout():
    session.user = None
    return 'Bye! <a href="/">Go back</a>'
    
app.run(host='0.0.0.0')
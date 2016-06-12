#!/usr/bin/env python3

# ab -n 1000 -c 10 http://localhost:8080/hello/world
# ab -n 2 -c 2 http://127.0.0.1:8080/hello/world

import gevent.monkey
gevent.monkey.patch_all()

import sys
sys.path.insert(0, '..')
import canister
import time

can = canister.build('cgevent.config')

@can.get('/')
def index():
    if can.session.user:
        return "Hi " + str(can.session.user) + "!";
    else:
        err = bottle.HTTPError(401, "Login required")
        err.add_header('WWW-Authenticate', 'Basic realm="%s"' % 'private')
        return err

@can.get('/hello/<name>')
def hello(name):
    can.log.info('before')
    time.sleep(0.1)
    can.log.info('after')
    return "Hello {0}!".format(name) #template('<b>Hello {{name}}</b>!', name=name)

can.run()
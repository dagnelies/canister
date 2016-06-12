#!/usr/bin/env python3

# ab -n 1000 -c 10 http://localhost:8080/hello/world
# ab -n 2 -c 2 http://127.0.0.1:8080/hello/world

import gevent.monkey
gevent.monkey.patch_all()

import canister
import time
import bottle

can = canister.build('example.config')

@can.get('/')
def index():
    # Accessing session data
    sdata = can.session.data
    if 'counter' in can.session.data:
        sdata['counter'] += 1
    else:
        sdata['counter'] = 0
        
    # Logging something
    can.log.info('Hey!')
    can.log.warning('Ho!')
    
    return '<pre>Session id: %s\nCounter: %s</pre>' % (can.session.id, can.session.data['counter'])


can.run()
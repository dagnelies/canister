#!/usr/bin/env python3

# ab -n 1000 -c 10 http://localhost:8080/hello/world
# ab -n 2 -c 2 http://127.0.0.1:8080/hello/world

import gevent.monkey
gevent.monkey.patch_all()

import sys
sys.path.insert(0, '..')
import canister
import time
import bottle
import os.path

can = canister.build('upload.config')

@can.get('/')
@bottle.view('upload.html')
def index():
    pass
    
@can.route('/upload', method='POST')
def do_upload():
    upload = bottle.request.files.get('upload')
    upload.save('uploads/' + upload.filename)
    return 'OK'
    
can.run()
Canister
========

Canister is a simple wrapper around bottle, providing:

- file based configuration
- logging
- sessions (server side, based on a `session_id` cookie)
- ssl support (for gevent or cherrypy as server adapter at least)
- can serve all files in a `static_path` directory out of the box
- CORS for cross-domain REST APIs
- authentication through basic auth or bearer token (oauth2)

### Usage

```
import canister
import bottle

can = canister.build('example.config')

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
    can.log.info('Hey!')
    time.sleep(0.1)
    can.log.info('Ho!')
    return "Hello {0}!".format(name) #template('<b>Hello {{name}}</b>!', name=name)

can.run()
```

### Logs

### Sessions

### Authentication

### SSL

### Serving a directory

### Websockets

### CORS
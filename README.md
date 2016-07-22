Canister
========

Canister is a simple plugin for bottle, providing:

- formatted logs
- url and form params unpacking
- sessions (server side) based on a `session_id` cookie
- authentication through basic auth or bearer token (OAuth2)
- CORS for cross-domain REST APIs

#### *Note: the `examples` directory is outdated.*

### Usage

```
import bottle
import canister
from bottle import session

app = bottle.Bottle()
app.install(canister.Canister())


@app.get('/')
def index(foo=None):
    if 'counter' in session.data:
        session.data['counter'] += 1
    else:
        session.data['counter'] = 0
        
    return '''
        <pre>
            Session sid: %s
            Session user: %s
            Session data: %s 
            "?foo=...": %s
        </pre>
    ''' % (session.sid, session.user, session.data, foo)
    
app.run()
```

### Sample config file

```
[canister]

# The logs directory
log_path = ./logs/
# Logging levels: DISABLED, DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = INFO
# Log older than that will be deleted
log_days = 30

# how long the session data will still be available after the last access, in seconds
session_timout = 3600

# applies CORS to responses, write * to allow AJAX requests from anywhere
#CORS = *

# Basic auth
auth_basic_username = alice
auth_basic_encryption = clear
auth_basic_password = my-secret

# ...or alternatively, if you dislike putting your plain text password in the config:
# auth_basic_encryption = sha256
# auth_basic_password = 186ef76e9d6a723ecb570d4d9c287487d001e5d35f7ed4a313350a407950318e


# Auth using JWT (for OAuth2)
auth_client_id = ABC
# accepted encodings are "clear", "base64std" or "base64url"
auth_jwt_encoding = base64url
auth_jwt_secret = my-secret
```

### Logs

If not otherwise configured, logs will be written in the `logs` directory. They look like this:

```
2016-07-02 09:38:31,022 INFO     [MainThread]   ============
2016-07-02 09:38:31,022 INFO     [MainThread]   Initializing
2016-07-02 09:38:31,022 INFO     [MainThread]   ============
2016-07-02 09:38:31,022 INFO     [MainThread]   python version: 3.4.3 (default, Oct 14 2015, 20:28:29) 
2016-07-02 09:38:31,022 INFO     [MainThread]   bottle version: 0.12.9
2016-07-02 09:38:31,022 INFO     [MainThread]   ------------------------------------------
2016-07-02 09:38:31,022 INFO     [MainThread]   ...all config params...
2016-07-02 09:38:31,022 INFO     [MainThread]   ------------------------------------------
2016-07-02 09:38:33,216 INFO     [149.172.44.162-...]   GET http://localhost:8080/
2016-07-02 09:38:33,216 INFO     [149.172.44.162-VJ8zq5]   Session id: VJ8zq5Gq55cVstAJg4zcC2E1
2016-07-02 09:38:33,217 INFO     [149.172.44.162-VJ8zq5]   Response: 200 (1ms)
```

You will get one such log file each day, like `log.2016-07-02`.

You can also log messages in your code like this:
```
@app.get('/')
def index():
    app.log.info('Hey!')
    return 'Ho!'
```

The logging uses the common `logging` module and is thread safe.
When serving requests, the corresponding thread also gets renamed according to the client IP and the start of its session ID.
This can be seen in the logs `[149.172.44.162-VJ8zq5]` in order to be able to easely follow client-server "discussions" over a longer timespan.

### URL and form params unpacking

### Sessions


### Authentication

### CORS

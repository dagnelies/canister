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

app = bottle.Bottle()
app.config.load_config('my_config')
app.install(canister.Canister())

@app.get('/')
def index():
    return 'Hi!'
    
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

### Security

One of the common security flaws of web apps is Cross Site Request Forgery (https://en.wikipedia.org/wiki/Cross-site_request_forgery)

Either:
- provide auth-creditentials

Or:
- provide a HTTP-Only cookie containing your session ID (to prove your're authenticated and prevent XSS, done by the server)
- and provide a session token as parameter or in a "X-Csrf-Token" header (to prove it comes from your Browser and prevent CSFR, must be done client side through javascript)

---

Provide HTTP-Only cookie + check Referer Header.
How does this prevent CSRF?
- if the request doesn't come from the browser, the cookie/session-id is unknown
- if it comes from the browser, we can ensure it comes from the site itself
 
...the only issue is in case the header is removed (because of a privacy proxy or plugin, but I think it's pretty seldom)

...the issue is that any other method requires client side stuff in the page (through hidden fields, request parameters or setting specific headers through javascript)

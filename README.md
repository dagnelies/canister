Canister
========

Canister is a simple plugin for bottle, providing:

- formatted logs
- url and form params unpacking
- sessions (server side) based on a `session_id` cookie
- authentication through basic auth or bearer token (OAuth2)
- CORS for cross-domain REST APIs

### Usage

```
import bottle
import canister.Canister as Can

app = bottle.Bottle()
app.config.load_config('example.config')
app.install(Can())


@app.get('/')
def index():
    return 'Hi!'
    
app.run()
```

### Sample config file

```
```

### Logs

### URL and form params unpacking

### Sessions

### Authentication

### CORS
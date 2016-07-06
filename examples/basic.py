import sys
sys.path.insert(0, '..')
import bottle
import canister

app = bottle.Bottle()
app.config.load_config('example.config')
app.install(canister.Canister())


@app.get('/')
def index():
    return 'Session id: %s\n' % bottle.request.session_id
    
app.run(host='0.0.0.0')
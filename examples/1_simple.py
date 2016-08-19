import sys
# just for the tests, to fetch the development version of canister in the parent directory
sys.path.insert(0, '..')

import bottle
import canister
from canister import session

app = bottle.Bottle()
app.install(canister.Canister())


@app.get('/')
def index():
    return 'It works!'
    
app.run(host='0.0.0.0')
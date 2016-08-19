import sys
# just for the tests, to fetch the development version of canister in the parent directory
sys.path.insert(0, '..')

import bottle
import canister
from canister import session

app = bottle.Bottle()
app.install(canister.Canister())


@app.get('/')
def index(foo=None, bar=None):
    return '''
        <pre>
            Function parameters are automatically extracted from the request if present.
            foo: %s
            bar: %s
        </pre>
        <a href="/?foo=Foooooooo&bar=Baaaaaaaar">/?foo=Foooooooo&bar=Baaaaaaaar</a>
    ''' % (foo,bar)
    
app.run(host='0.0.0.0')
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
    if 'counter' in session.data:
        session.data['counter'] += 1
    else:
        session.data['counter'] = 0
        
    return '''<pre>
        Refresh the page to see the counter increase.
        Session sid: %s
        Session data: %s 
    </pre>''' % (session.sid, session.data)
    
app.run(host='0.0.0.0')
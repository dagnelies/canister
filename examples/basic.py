import sys
sys.path.insert(0, '..')
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
    
app.run(host='0.0.0.0', debug=True)
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
    app.log.debug('Some debug message')
    app.log.info('Some info message')
    app.log.warn('Some warning message')
    app.log.error('Some error message')
    app.log.critical('Big problem!')
    
    return '''<pre>
    When "debug=true" (default) is written in the config, all logs go to the console.
    If "debug=false" is set, they are written to a rotating log file.
    This flag is also separate from bottle's "run(..., debug=True|False) since the plugin is initialized BEFORE bottle is run.
    Note that even when the log is written, the underlying WSGI server may still write to stdout, stderr or elsewhere.
    </pre>'''
    
app.run(host='0.0.0.0')
import sys
# just for the tests, to fetch the development version of canister in the parent directory
sys.path.insert(0, '..')

import bottle
import canister
from canister import session

app = bottle.Bottle()
app.config.load_config('2_logging.config')
app.install(canister.Canister())


@app.get('/')
def index():
    app.log.debug('Some debug message')
    app.log.info('Some info message')
    app.log.warn('Some warning message')
    app.log.error('Some error message')
    app.log.critical('Big problem!')
    
    return '''<pre>
    Without config, all logs go to the console.
    If "log_path=..." is set, they are written to a rotating log file.
    Note that even when the log is written, the underlying WSGI server may still write to stdout, stderr or elsewhere.
    </pre>'''
    
app.run(host='0.0.0.0')
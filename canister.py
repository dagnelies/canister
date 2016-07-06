"""
Canister is a simple plugin for bottle, providing:

- formatted logs
- url and form params unpacking
- sessions (server side) based on a `session_id` cookie
- authentication through basic auth or bearer token (OAuth2)
- CORS for cross-domain REST APIs
"""
import sys
import logging
import logging.handlers
import bottle
import threading
import base64
import os
import os.path
import configparser
import jwt
import hashlib
import inspect
import time


class TimedDict(dict):
    def __init__(self):
        self._items = {}
        
    def __getitem__(self, key):
        (t, val) = self._items[key]
        t = time.time()
        self._items[key] = (t, val)
        return val
        
    def __setitem__(self, key, val):
        t = time.time()
        self._items[key] = (t, val)
        
    def __contains__(self, key):
        return (key in self._items)
        
    def __delitem__(self, key):
        del self._items[key]
        
    def keys(self):
        return self._items.keys()
        
    def values(self):
        for t,val in self._items.values():
            yield val
    
    def items(self):
        for (k, (t,val)) in self._items.items():
            yield (k, val)
            
    def prune(self, age):
        now = time.time()
        survivors = {}
        for (k, (t,val)) in self._items.items():
            if now - t < age:
                survivors[k] = (t,val)
        self._items = survivors
        
        

        
def _buildLogger(config):
    level = config.get('canister.log_level', 'INFO')
    path = config.get('canister.log_path', './logs/')
    days = int( config.get('canister.log_days', '30') )
    log = logging.getLogger('canister')
    if level.upper() not in ['DISABLED', 'FALSE', 'NONE']:
        os.makedirs(path, exist_ok=True)
        log.setLevel(level) 
        h = logging.handlers.TimedRotatingFileHandler( os.path.join(path, 'log'), when='midnight', backupCount=int(days))
        f = logging.Formatter('%(asctime)s %(levelname)-8s [%(threadName)s]   %(message)s')
        h.setFormatter( f )
        log.addHandler( h )
        
    return log



def _buildAuthBasic(config):
    username = config.get('canister.auth_basic_username', None)
    password = config.get('canister.auth_basic_password', None)
    encryption = config.get('canister.auth_basic_encryption', 'clear').lower() # clear or sha256
    
    if not username or not password:
        return None
        
    def validate(token):
        user, pwd = base64.b64decode(token).decode('utf-8').split(':', 1)
        if user != username:
            return None
        elif encryption == 'clear' and password == pwd:
            return user
        elif encryption == 'sha256' and password == hashlib.sha256(pwd):
            return user
        else:
            return None
    
    return validate
    


def _buildAuthJWT(config):
    client_id = config.get('canister.auth_jwt_client_id', None)
    secret = config.get('canister.auth_jwt_secret', None)
    encoding = config.get('canister.auth_jwt_encoding', 'clear').lower() # clear, base64, or base64url
    
    if not client_id or not secret:
        return None
    
    if encoding == 'base64std': # with + and /
        secret = base64.standard_b64decode(secret)
    elif encoding == 'base64url': # with - and _
        secret = base64.urlsafe_b64decode(secret)

    def validate(token):
        profile = jwt.decode(token, secret, audience=client_id)
        return profile
    
    return validate
    
    
class SessionCache:
    def __init__(self, interval=60, max_age=3600, log=None):
        self._lock = threading.Lock()
        self._cache = TimedDict()
        
        def prune():
            while True:
                time.sleep(interval)
                with self._lock:
                    n = self._cache.prune(max_age)
                    if log:
                        log.debug('%d expired sessions pruned' % n)
            
        cleaner = threading.Thread(name="SessionCleaner", target=prune)
        cleaner.deamon=True
        cleaner.start()
        
    def get(self, sid):
        if not sid:
            return None
            
        with self._lock:
            if sid in self._cache:
                return self._cache[sid]
            else:
                return None
    
    def create(self):
        sid = base64.b64encode(os.urandom(18)).decode('ascii')
        data = {}
        with self._lock:
            self._cache[sid] = data
        
        return (sid, data)
    
    def delete(self, sid):
        with self._lock:
            del self._cache[sid]
            
class Canister:
    name = 'canister'
    api = 2

    def __init__(self):
        pass
    
    def setup(self, app):
        
        #if 'canister' not in app.config:
        #    raise Exception('Canister requires a configuration file. Please refer to the docs.')
        
        config = app.config
        
        log = _buildLogger(config)
        
        log.info('============')
        log.info('Initializing')
        log.info('============')
        
        log.info('python version: ' + sys.version)
        log.info('bottle version: ' + bottle.__version__)
        
        log.info('------------------------------------------')
        for k,v in app.config.items():
            log.info('%-30s = %s' % (k,v))
        log.info('------------------------------------------')
        
        
        self.app = app
        self.log = log
        app.log = log
        
        self.sessions = SessionCache()
        self.session_secret = base64.b64encode(os.urandom(30)).decode('ascii')
        
        self.auth_basic = _buildAuthBasic(config)
        if self.auth_basic:
            log.info('Basic authentication enabled.') 
        
        self.auth_jwt = _buildAuthJWT(config)
        if self.auth_jwt:
            log.info('JWT authentication enabled.')
        
        self.cors = config.get('canister.CORS', None)
        if self.cors and self.cors.lower() == 'false':
            self.cors = None
        
    def apply(self, callback, route):
        
        log = self.log
        
        def wrapper(*args, **kwargs):
            
            start = time.time()
            
            req = bottle.request
            res = bottle.response
            
            # thread name = <ip>-....
            threading.current_thread().name = req.remote_addr + '-...'
            log.info(req.method + ' ' + req.url)
            
            # session
            req.session_id = req.get_cookie('session_id', secret=self.session_secret)
            req.session = self.sessions.get(req.session_id)
            
            if req.session != None:
                log.info('Session found: ' + req.session_id)
            else:
                req.session_id, req.session = self.sessions.create()
                log.info('Session created: ' + req.session_id)
                res.set_cookie('session_id', req.session_id, secret=self.session_secret)
                
            # thread name = <ip>-<session_id[0:6]>
            threading.current_thread().name = req.remote_addr + '-' + req.session_id[0:6]
            
            
            # user
            req.user = None
            auth = req.headers.get('Authorization')
            if auth:
                tokens = auth.split()
                if len(tokens) != 2:
                    self.log.warning('Invalid or unsupported Authorization header: ' + auth)
                    return None
                
                if self.auth_basic and tokens[0].lower() == 'basic':
                    req.user = self.auth_basic( tokens[1] )
                    
                elif self.auth_jwt and tokens[0].lower() == 'bearer':
                    req.user = self.auth_jwt( tokens[1] )
                    
                if req.user:
                    self.log.info('Logged in as: ' + str(req.user))
        
            # args unpacking
            sig = inspect.getargspec(callback)
            
            for a in sig.args:
                if a in req.params:
                    kwargs[a] = req.params[a]
                    
            result = callback(*args, **kwargs)
            
            if self.cors:
                res.headers['Access-Control-Allow-Origin'] = self.cors
            
            elapsed = time.time() - start
            
            if elapsed > 1:
                log.warn('Response: %d (%dms !!!)' % (res.status_code, 1000*elapsed))
            else:
                log.info('Response: %d (%dms)' % (res.status_code, 1000*elapsed))
            return result
            
        return wrapper
        
        
    def close(self):
        pass

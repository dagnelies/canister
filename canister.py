"""
This is a wrapper around bottle, providing:

- file based configuration
- logging
- sessions (server side) based on a `session_id` cookie
- ssl support (for gevent or cherrypy as server adapter at least)
- serves all files in the `static_path` directory out of the box
- CORS for cross-domain REST APIs
- authentication through basic auth or bearer token
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

def getLogger(level, path, days, notify, **kwargs):
    log = logging.getLogger('canister')
    if level.upper() != 'DISABLED':
        os.makedirs(path, exist_ok=True)
        log.setLevel(level) 
        h = logging.handlers.TimedRotatingFileHandler( os.path.join(path, 'log'), when='midnight', backupCount=int(days))
        f = logging.Formatter('%(asctime)s %(levelname)-8s [%(threadName)s]   %(message)s')
        h.setFormatter( f )
        log.addHandler( h )
        if notify:
            pass
            # TODO: add email notifier with SMTPHandler + QueueHandler
    return log
    

def getRequestsLogger(level, path, days, requests, **kwargs):
    log = logging.getLogger('requests')
    if level.upper() != 'DISABLED' and requests.lower() == 'true':
        log.setLevel(level) 
        h = logging.handlers.TimedRotatingFileHandler( os.path.join(path, 'requests'), when='midnight', backupCount=int(days))
        log.addHandler( h )
    return log
        
def build(config_path):
    
    config = configparser.ConfigParser()
    with open(config_path) as f:
        config.read_file(f)
    
    can = bottle.Bottle()
    
    
    log = getLogger(**config['logs'])
    log_req = getRequestsLogger(**config['logs'])
    
    log.info('============')
    log.info('Initializing')
    log.info('============')
    
    log.info('python version: ' + sys.version)
    log.info('bottle version: ' + bottle.__version__)
    
    log.info('------------------------------------------')
    for s in config.sections():
        for p in config[s]:
            log.info('%-23s = %s' % (s + '.' + p, config[s][p]) )
    log.info('------------------------------------------')
    
    
    sessions = {}
    session_secret = base64.b64encode(os.urandom(30)).decode('ascii')
    can.session = threading.local()
    
    auth_basic_username = config.get('auth_basic', 'username', fallback=None)
    auth_basic_password = config.get('auth_basic', 'password', fallback=None)
    auth_basic_enc = config.get('auth_basic', 'password_enc', fallback='clear').lower()
    
    if auth_basic_username and auth_basic_password:
        log.info('Enabling basic authentication for: ' + auth_basic_username)
        
    auth_jwt_secret = config.get('auth_jwt', 'secret', fallback=None)
    
    if auth_jwt_secret:
        log.info('Enabling JWT bearer token authentication')
        auth_jwt_secret = base64.urlsafe_b64decode(auth_jwt_secret)
    
    def getUser(auth):
        tokens = auth.split()
        if len(tokens) != 2:
            log.warning('Invalid or unsupported Authorization header: ' + auth)
            return None
        
        if auth_basic_username and tokens[0].lower() == 'basic':
            user, pwd = base64.b64decode( tokens[1] ).decode('utf-8').split(':', 1)
            if user != auth_basic_username:
                return None
            elif auth_basic_enc == 'clear' and auth_basic_password == pwd:
                return user
            elif auth_basic_enc == 'sha256' and auth_basic_password == hashlib.sha256(pwd):
                return user
            else:
                return None
            
        elif auth_jwt_secret and tokens[0].lower() == 'bearer':
            profile = jwt.decode(tokens[1], auth_jwt_secret)
            return profile
        
    @can.hook('before_request')
    def before():
        req = bottle.request
        res = bottle.response
        
        # thread name = <ip>-....
        threading.current_thread().name = can.remote_addr + '-....'
        log.info(req.method + ' ' + req.url)
        
        can.session.id = None 
        can.session.user = None
        can.session.data = None
        
        can.session.id = req.get_cookie('session_id', secret=session_secret)
        if not can.session.id or (can.session.id not in sessions):
            # either there is no ID or it's been purged from the sessions
            can.session.id = base64.b64encode(os.urandom(18)).decode('ascii')
            res.set_cookie('session_id', can.session.id, secret=session_secret, httponly=True)
            sessions[can.session.id] = {}
            
        # thread name = <ip>-<session_id[0:4]>
        threading.current_thread().name = can.remote_addr + '-' + can.session.id[0-4]
        log.info('Session id: ' + can.session.id)
        
        # set data
        can.session.data = sessions[can.session.id]
        
        auth = req.headers.get('Authorization')
        if auth:
            try:
                log.debug('Attempting authentication for: ' + auth)
                user = getUser(auth)
                can.session.user = user
                if user:
                    log.info('Logged in as: ' + user)
            except Exception as ex:
                log.warning('Authentication failed: ' + str(ex))
                
            
            
         
    @can.hook('after_request')
    def after():
        res = bottle.response
        # TODO: is there a way to log the start of the response?
        log.info(res.status_line)
    
    
    def logout(user):
        # TODO: remove cookie
        # TODO: clear session
        pass
    
    def run():
        
        static_path = config.get('views', 'static_path', fallback=None)
        if static_path:
            @can.get('/<path:path>')
            def serve(path):
                return bottle.static_file(path, root=static_path)

        log.info('Starting...')
        bottle.run(can, log=log_req, error_log=log, **config['bottle'])
    
    can.log = log
    can.run = run
    can.logout = logout
    
    return can
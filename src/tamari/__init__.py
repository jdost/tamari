from db import connect
from settings import settings
import hashlib

db = connect()


class ReverseProxy(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

def cleanup():
    db.cleanup()


def pwhash(password):
    ''' pwhash:
    simple function that handles creating the password hashes for storage and
    comparison
    '''
    pwhash = hashlib.sha224(password)
    pwhash.update(app.secret_key)
    return pwhash.hexdigest()

from flask import Flask
import tamari.session

app = Flask(__name__)
app.session_interface = tamari.session.Sessions(db)
app.secret_key = settings["secret_key"]
app.debug = settings["debug"]
app.db = db


import tamari.user, tamari.thread
if __name__ == '__main__':
    app.run()

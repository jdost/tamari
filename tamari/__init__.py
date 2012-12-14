import settings
import database
import hashlib

__version__ = "0.3"
# List of the modules to import
__all__ = ["user", "thread", "api", "forum"]


def cleanup():
    from .database import Forum
    database.cleanup()
    app.endpoint('root', '/forum/' + str(Forum.get_root()))


def password_hash(password):
    ''' password_hash:
    simple function that handles creating the password hashes for storage and
    comparison
    '''
    pwhash = hashlib.sha224(password)
    pwhash.update(app.secret_key)
    return pwhash.hexdigest()

# Webapp initiliazation
from .decorators import TamariFlask
from . import session
# TamariFlask is in decorators, just extended version of flask.Flask
app = TamariFlask(__name__)
app.session_interface = session.SessionHandler()
app.secret_key = settings.SECRET_KEY
app.debug = settings.DEBUG
app.jinja_env.line_statement_prefix = '%'
app.__version__ = __version__
# This just imports all of the webapps modules (defined in __all__)
from importlib import import_module
map(lambda module: import_module("." + module, __name__), __all__)

from db import connect
from settings import settings
import hashlib

db = connect()


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


import tamari.user, tamari.thread
if __name__ == '__main__':
    app.run()

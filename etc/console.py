from tamari import app
from tamari.database import Forum, Permission, Session, Thread, User

import code

try:
    import readline
except ImportError:
    pass
else:
    readline.parse_and_bind("tab:complete")

app.config['SERVER_NAME'] = 'localhost'
with app.app_context():
    code.interact('''
preimported: app (Tamari application)
models available: Forum Permission Session Thread User
''', local=locals())

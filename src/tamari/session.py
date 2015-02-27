''' session.py
Collection of functions that deal with the session handling for the Flask app,
sessions exist in the mongo db and are created with a set of defaults dictated
in the settings file.
'''
from flask.sessions import SessionInterface, SessionMixin
from . import settings
from .database import Session as Sessions

SESSION_KEY = settings.SESSION_KEY


class Session(dict, SessionMixin):
    ''' Session
    wrapper class for the created session, just makes sure the session is
    initialized to a specific default (as specified in the settings)
    '''
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self["permissions"] = []
        self.update(settings.SESSION_DEFAULTS)

    def clear(self, *args, **kwargs):
        Sessions.remove(self['_id'])
        return dict.clear(self, *args, **kwargs)


class SessionHandler(SessionInterface):
    ''' SessionHandler
    class implementing the SessionInterface for Flask to store the sessions in
    the database, this could always use plenty of work.
    '''
    def __init__(self):
        pass

    def open_session(self, app, request):
        ''' SessionHandler::open_session
        if no key is stored in the cookies, returns None, otherwise will return
        the data packet stored in the database using the key retrieved from the
        cookie.
        '''
        if SESSION_KEY not in request.cookies:
            return Session()
        session_id = request.cookies[SESSION_KEY]
        session = Sessions.get(session_id)
        return session if session else Session()

    def save_session(self, app, session, response):
        ''' Sessions::save_session
        saves the session packet into the database and checks if this is a new
        session packet or not (if the is an id in the packet), if it is new,
        the id will be stored as a cookie for future lookup
        '''
        id = Sessions.save(session)
        response.set_cookie(SESSION_KEY, value=id)

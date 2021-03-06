''' api.py
Contains routes and actions specific to the REST API, things that really don't
fall into any larger category are mostly what go into here.  This includes the
discovery route, the settings modification, and the version route.
'''
from . import app
from .decorators import datatype
from flask import request, session
import httplib
# This is just a set of keys that can't be set via settings
prohibited_settings = ["id", "_id"]

route = "/settings"
app.endpoint(name='settings', route=route)


@app.put(route)
@datatype
def set_settings():
    ''' set_settings -> POST /settings
        POST: [key]=[value]
    Sets session settings, things like default packet parts, page sizes, etc,
    mostly acts as a client controlled way of establishing default params for
    various API calls without needing to explicitly set them for ever call.
    '''
    for key in request.form:
        if key not in prohibited_settings:
            session[key] = request.form[key]
    return httplib.ACCEPTED


@app.get(route)
@datatype
def view_settings():
    ''' view_settings -> GET /settings

    Gets the current settings, really just a reader method for a client to be
    able to review the current values
    '''
    settings = {}
    for key in session:
        if key not in prohibited_settings:
            settings[key] = session[key]

    return settings


@app.get('/')
@datatype("index.html")
def index():
    ''' index -> GET /

    Discovery call, returns a list of the starting endpoints to allow for the
    dynamic discovery of API consumers, no more hard coded URL paths in the
    code!
    '''
    return app.endpoints, httplib.OK


@app.get('/version')
@datatype
def get_version():
    ''' get_version -> GET /version

    Returns the version of the app, useful for compatibility checks of APIs
    '''
    return app.__version__

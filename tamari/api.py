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
@datatype
def index():
    return app.endpoints, httplib.OK

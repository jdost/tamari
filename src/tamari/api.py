from tamari import app
from flask import request, session
import httplib
import json


# This is just a set of keys that can't be set via settings
prohibited_settings = ["id", "_id"]


@app.route('/settings', methods=['POST'])
def set_settings():
    ''' set_settings -> POST /settings
    Sets session settings, things like default packet parts, page sizes, etc,
    mostly acts as a client controlled way of establishing default params for
    various API calls without needing to explicitly set them for ever call.
    '''
    for key in request.form:
        if key not in prohibited_settings:
            session[key] = request.form[key]
    return "", httplib.OK


@app.route('/settings', methods=['GET'])
def view_settings():
    ''' view_settings -> GET /settings
    Gets the current settings, really just a reader method for a client to be
    able to review the current values
    '''
    settings = {}
    for key in session:
        if key not in prohibited_settings:
            settings[key] = session[key]

    return json.dumps(settings)

''' decorators.py
This file defines the helper decorator functions, these are some application
wide decorators for routes to help with common tasks and scenarios for dealing
with the web requests.
'''
import json
import datetime
import time
from functools import wraps
from bson.objectid import ObjectId
from flask import request, make_response, session, abort, render_template, \
    Flask, url_for
from werkzeug import BaseResponse
from . import settings
import httplib


def intersect(a, b):
    ''' intersect
    Returns a boolean if an item in <list> a is also in <list> b
    '''
    return reduce(lambda x, y: x or y, [i in a for i in b])


def html_base():
    ''' html_base
    Generates a general base set of information for the HTML page rendering.
    '''
    return {
        "logged_id": 'id' in session
    }


class TamariFlask(Flask):
    ''' TamariFlask:
    This is just an expansion on the Flask app class to add fancier decorators
    to the app
    '''
    def __init__(self, *args, **kwargs):
        self.endpoints = {}  # This is the storage property for the endpoints
        if settings.DEBUG:
            if 'static_folder' not in kwargs and 'folder' in settings.STATIC:
                kwargs['static_folder'] = settings.STATIC['folder']
            if 'static_url_path' not in kwargs and 'path' in settings.STATIC:
                kwargs['static_url_path'] = settings.STATIC['path']

        self.__dict__.update({
            method: self.__shorthand({'methods': [method.upper()]})
            for method in ["get", "post", "put"]})

        return Flask.__init__(self, *args, **kwargs)

    def endpoint(self, name, route):
        ''' endpoint:
        Stores an alias for a specific endpoint of the application, this is
        used for the dynamic discovery of the application.
        '''
        self.endpoints[name] = {
            'url': route,
            'methods': []
        }

    def route(self, *args, **kwargs):
        ''' route:
        Wraps the regular Flask.route functionality, takes the methods out of
        the route and adds them to the dictionary of endpoints, used for the
        discovery request.
        '''
        route = args[0]
        for info in self.endpoints.values():
            if info['url'] == route:
                info['methods'] += kwargs['methods']
                break

        return Flask.route(self, *args, **kwargs)

    def __shorthand(self, defaults):
        ''' decorator helper method:
        Helps the create shorthand decorators for making the method setting
        simpler.  Just used to override the kwargs of a route to some
        established set.
        '''

        def new_route(*args, **kwargs):
            kwargs.update(defaults)
            return lambda f: self.route(*args, **kwargs)(f)
        return new_route


class JSONEncoder(json.JSONEncoder):
    ''' JSONEncoder
    An extended json.JSONEncoder, used to customize the encoding of the data
    packets (dicts or lists) into JSON, just catches various types and beyond
    the basic types and handles their JSON representation (examples are things
    like python's datetime or the bson.objectid used for indexing in mongo).
    '''
    DATE_FORMATS = {
        'iso': lambda date: date.isoformat(),
        'epoch': lambda date: time.mktime(date.timetuple())
    }

    def date_format(self, obj):
        if 'date_format' not in session:
            return str(obj)
        if session['date_format'] not in self.DATE_FORMATS:
            return obj.strftime(session['date_format'])
        return self.DATE_FORMATS[session['date_format']](obj)

    def default(self, obj):
        if isinstance(obj, ObjectId):  # ObjectId used in mongo
            return str(obj)
        elif isinstance(obj, datetime.datetime):  # datetime used for dates
            return self.date_format(obj)
        return json.JSONEncoder.default(self, obj)


JSON_KWARGS = {
    "cls": JSONEncoder,
    "separators": (',', ':')
}


def datatype(template=None):
    ''' datatype decorator:
    This decorator function is used to handle formatting and packaging a
    response coming out of a handler.  It will handle different scenarios and
    produce the proper format of output.  If the output of the route is a
    dictionary, it is assumed to be a data packet and will be formatted based
    on the HTTP Accept header, if it is a number, it is treated like a HTTP
    status code.

    argument(optional) template file to render html requests with

    ex:
        @datatype('some_function.html')
        @app.route('/some/path')
        def some_function():  # this will be converted into a proper response
            return { "foo": "bar" }
    '''
    mimetypes = {
        "application/json": lambda d: json.dumps(d, **JSON_KWARGS)
    }
    if type(template) is str:
        mimetypes["text/html"] = lambda d: \
            render_template(template, **dict(d.items() + html_base().items()))
    default = 'application/json'

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            request.is_html = request.accept_mimetypes.accept_html
            data = func(*args, **kwargs)
            status_code = httplib.OK
            if type(data) is tuple:  # if multiple, break apart
                status_code = data[1]
                data = data[0]

            if type(data) is int:  # if int, treat it like a status code
                response = make_response("", data)
            elif type(data) is dict or type(data) is list:
                # if it is a dict or list, treat like data packet
                callback = request.args.get('callback', False)
                if callback:  # if has a callback parameter, treat like JSONP
                    data = str(callback) + "(" + \
                        mimetypes['application/json'](data) + ");"
                    response = make_response(data, status_code)
                    response.mimetype = 'application/javascript'
                else:  # Non-JSONP treatment
                    best = request.accept_mimetypes. \
                        best_match(mimetypes.keys())
                    data = mimetypes[best](data) if best \
                        else mimetypes[default](data)
                    response = make_response(data, status_code)
                    response.mimetype = best if best else default
            elif isinstance(data, BaseResponse):  # if it is a Response, use it
                response = data
            else:  # otherwise, treat it like raw data
                response = make_response(data, status_code)

            return response
        return decorated_function

    if hasattr(template, '__call__'):  # if no template was given
        return decorator(template)
    else:
        return decorator


def require_permissions(func=None, forum=False, thread=False, post=False):
    ''' require_permissions decorator:
    This decorator function is used to flag routes as endpoints that require
    the user to be logged in.  This is to easily take care of handling all of
    the checks on handlers that expect credentials to be in the session for
    the actions to be taken care of.

    ex:
        @require_permissions(roles.ADMIN)
        @app.route('/some/path')
        def some_function():  # Won't run if user is not an admin
            return { "foo": "bar" }
    '''
    #from . import logger
    from .database import Permission as Perms

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if 'id' not in session:
                #logger.warning(
                    #"Attempting to access without being logged in.")
                abort(httplib.UNAUTHORIZED)
            elif (forum and not Perms.check_forum(kwargs['forum_id'])) or \
                 (thread and not Perms.check_thread(kwargs['thread_id'])) or \
                 (post and not Perms.check_post(kwargs['post_id'])):
                #logger.warning(
                    #"Attempting to access without sufficient " +
                    #"permissions.  Has: {} Needs: {}",
                    #session['rights'], forum_id)
                abort(httplib.UNAUTHORIZED)
            return func(*args, **kwargs)
        return decorated_function

    return decorator if not func else decorator(func)


def paginate(func):
    ''' paginate decorator:
    This decorator function is used to handle the pagination of long lists of
    models.  It pulls the page count and page size from either the request
    arguments or the session and passes them into the view function.  It then
    adds the 'Link' header to the response.

    Assumes the wrapped function takes kwargs of 'page' and 'per_page' to
    handle the limiting and offsetting of the query.
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        page = int(request.args.get('page', 0))
        per_page = request.args.get('per_page', session.get('page_size', 25))

        kwargs['page'] = page
        kwargs['per_page'] = int(per_page)

        links = []
        vargs = request.view_args.copy()
        if 'per_page' in request.args:
            vargs['per_page'] = per_page

        if page > 0:
            vargs['page'] = page - 1
            links.append(
                "<" + url_for(request.endpoint, **vargs) + ">; rel=\"prev\"")

        vargs['page'] = page + 1
        links.append(
            "<" + url_for(request.endpoint, **vargs) + ">; rel=\"next\"")

        response = func(*args, **kwargs)
        response.headers.add('Link', ", ".join(links))

        return response

    return decorated_function

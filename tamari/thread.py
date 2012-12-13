import httplib
import datetime
from . import app
from .decorators import datatype, require_permissions, paginate
from .database import errors, Thread

from flask import request, session


@app.get('/thread/<thread_id>')
@paginate
@datatype
def get_thread(thread_id, page=0, per_page=25):
    ''' get_thread -> GET /thread/<thread_id>

    Retrieves the thread specified by the route arg <thread_id>.  Will paginate
    the output based on the paginate decorator.  If the thread_id does not
    correspond to a thread on the system, a NOT_FOUND will be returned,
    otherwise the thread packet will be returned.
    '''
    try:
        thread = Thread.get(
            thread_id=thread_id, limit=per_page, start=(page * per_page))
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND

    return thread if isinstance(thread, dict) else httplib.NOT_FOUND


@app.put('/thread/<thread_id>')
@datatype
@require_permissions(thread=True)
def edit_thread(thread_id):
    ''' edit_thread -> PUT /thread/<thread_id>
        PUT title=[string]

    Tries to modify an existing thread specified by the route arg <thread_id>.
    If the thread_id does not correspond to an item in the database, will
    return a NOT_FOUND.  Otherwise will apply the changes in the PUT data to
    the existing thread object and return an ACCEPTED with the new thread
    object.
    '''
    if 'title' not in request.form:
        return httplib.BAD_REQUEST

    title = request.form['title']
    try:
        thread = Thread.edit_thread(thread_id, user=session['id'], info={
            "title": title,
            "editted": datetime.datetime.utcnow()
        })
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return thread, httplib.ACCEPTED


@app.post('/thread/<thread_id>')
@datatype
@require_permissions
def replyto_thread(thread_id):
    ''' replyto_thread -> POST /thread/<thread_id>
        POST content=[string]

    Creates a post in reply to the thread specified by the <thread_id> route
    arg.  If the thread_id does not correspond to an existing thread, a
    NOT_FOUND will be returned.  The content passed in will be used to create
    a post done by the logged in user as specified by the session dict.  On
    successfully creating the object, a CREATED will be returned with the new
    post object.  If any information is missing, a BAD_REQUEST will be returned
    '''
    if 'content' not in request.form:
        return httplib.BAD_REQUEST

    content = request.form['content']
    try:
        post = Thread.reply(thread_id, {
            "content": content,
            "user": session["id"],
            "created": datetime.datetime.utcnow()
        })
    except errors.MissingInfoError as err:
        return str(err), httplib.BAD_REQUEST
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return post, httplib.CREATED


@app.put('/post/<post_id>')
@datatype
@require_permissions(post=True)
def edit_post(post_id):
    ''' edit_post -> PUT /post/<post_id>
        PUT content=[string]

    Attempts to apply changes to the post specified by the <post_id> route arg,
    if the post_id does not correspond to an existing post, a NOT_FOUND will be
    be returned.  If the modification succeeds, an ACCEPTED will be returned
    with the structure of the modified post.
    '''
    content = request.form['content']
    try:
        post = Thread.edit_post(post_id, user=session['id'], info={
            "content": content,
            "editted": datetime.datetime.utcnow()
        })
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return (post, httplib.ACCEPTED) if isinstance(post, dict) \
        else httplib.NOT_FOUND


@app.get('/post/<post_id>')
@datatype
def get_post(post_id):
    ''' get_post -> GET /post/<post_id>

    Retrieves the post specified by the <post_id> route arg.  If the post_id
    does not correspond to a post on the system, a NOT_FOUND will be returned.
    Otherwise the post object will be returned.
    '''
    try:
        post = Thread.get_post(post_id)
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return post if isinstance(post, dict) else httplib.NOT_FOUND

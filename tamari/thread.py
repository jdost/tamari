import httplib
import datetime
from . import app
from .decorators import datatype, require_permissions, paginate
from .database import errors, Thread

from flask import request, session, abort


@app.get('/thread/<thread_id>')
@paginate
@datatype
def get_thread(thread_id, page=0, per_page=25):
    ''' get_thread -> GET /thread/<thread_id>
    get the full thread based on the specified thread_id
    '''
    return Thread.get(thread_id=thread_id)


@app.put('/thread/<thread_id>')
@require_permissions(thread=True)
def edit_thread(thread_id):
    ''' edit_thread -> PUT /thread/<thread_id>
    If the user is the one who created the thread, will save edits to the
    thread details, otherwise tosses an error
    '''
    title = request.form['title']
    try:
        Thread.edit_thread(thread_id, session, {
            "title": title,
            "editted": datetime.datetime.utcnow()
        })
    except errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return thread_id, httplib.ACCEPTED


@app.put('/post/<post_id>')
@require_permissions(post=True)
def edit_post(post_id):
    ''' edit_post -> PUT /post/<post_id>
    '''
    content = request.form['content']
    try:
        id = Thread.edit_post(post_id, session, {
            "content": content,
            "editted": datetime.datetime.utcnow()
        })
    except errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return str(id), httplib.ACCEPTED


@app.get('/post/<post_id>')
@datatype
def get_post(post_id):
    ''' get_post -> GET /post/<post_id>
    '''
    return Thread.get_post(post_id)


@app.post('/thread/<thread_id>')
@datatype
def replyto_thread(thread_id):
    ''' replyto_thread -> POST /thread/<thread_id>
    Replies to the thread, creates another post in the thread
    '''
    content = request.form['content']
    id = Thread.reply(thread_id, {
        "content": content,
        "user": session["id"],
        "created": datetime.datetime.utcnow()
    })
    return str(id), httplib.CREATED

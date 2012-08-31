import json
import httplib
import datetime
import time
from tamari import app
from db import db_errors

db = app.db
from flask import request, session, abort


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if 'date_format' not in session:
                return str(obj)

            if session['date_format'] == 'iso':
                return obj.isoformat()
            elif session['date_format'] == 'epoch':
                return time.mktime(obj.timetuple())
            else:
                return obj.strftime(session['date_format'])
        return json.JSONEncoder.default(self, obj)


JSON_KWARGS = {
    "cls": DateEncoder,
    "separators": (',',':')
}


@app.route('/thread', methods=['GET'])
@app.route('/forum/<forum_id>/thread', methods=['GET'])
def get_threads(forum_id=None):
    ''' get_threads -> GET /thread
        get_threads -> GET /forum/<forum_id>/thread
    gets a list of the threads either from the root or a specific forum
    '''
    return json.dumps(db.Thread.get(forum=forum_id), **JSON_KWARGS)


@app.route('/thread/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    ''' get_thread -> GET /thread/<thread_id>
    get the full thread based on the specified thread_id
    '''
    return json.dumps(db.Thread.get(thread_id=thread_id), **JSON_KWARGS)


@app.route('/forum/<forum_id>/thread', methods=['POST'])
@app.route('/thread', methods=['POST'])
def create_thread(forum_id=None):
    ''' create_thread -> POST /thread
        create_thread -> POST /forum/<forum_id>/thread
    Creates a thread for the forum
    '''
    title = request.form['title']
    content = request.form['content']
    id = db.Thread.create({
        "title": title,
        "content": content,
        "user": session['id'],
        "created": datetime.datetime.utcnow(),
        "forum": forum_id
    })
    return str(id), httplib.CREATED


@app.route('/thread/<thread_id>', methods=['PUT'])
def edit_thread(thread_id):
    ''' edit_thread -> PUT /thread/<thread_id>
    If the user is the one who created the thread, will save edits to the
    thread details, otherwise tosses an error
    '''
    title = request.form['title']
    try:
        db.Thread.edit_thread(thread_id, session, {
            "title": title,
            "editted": datetime.datetime.utcnow()
        })
    except db_errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return thread_id, httplib.ACCEPTED


@app.route('/post/<post_id>', methods=['PUT'])
def edit_post(post_id):
    ''' edit_post -> PUT /post/<post_id>
    '''
    content = request.form['content']
    try:
        id = db.Thread.edit_post(post_id, session, {
            "content": content,
            "editted": datetime.datetime.utcnow()
        })
    except db_errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return str(id), httplib.ACCEPTED


@app.route('/post/<post_id>', methods=['GET'])
def view_post(post_id):
    ''' view_post -> GET /post/<post_id>
    '''
    return json.dumps(db.Thread.get_post(post_id), **JSON_KWARGS)


@app.route('/thread/<thread_id>', methods=['POST'])
def replyto_thread(thread_id):
    ''' replyto_thread -> POST /thread/<thread_id>
    Replies to the thread, creates another post in the thread
    '''
    content = request.form['content']
    id = db.Thread.reply(thread_id, {
        "content": content,
        "user": session["id"],
        "created": datetime.datetime.utcnow()
    })
    return str(id), httplib.CREATED

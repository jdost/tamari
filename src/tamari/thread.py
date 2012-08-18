import json
import httplib
import datetime
from tamari import app
from db import connect, db_errors

db = connect()
from flask import request, session, abort


@app.route('/thread/', methods=['GET'])
def get_threads():
    ''' get_threads -> GET /thread/
    gets a list of the threads
    '''
    return json.dumps({
        "threads": db.Thread.get()
    })


@app.route('/thread/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    ''' get_thread -> GET /thread/<thread_id>
    get the full thread based on the specified thread_id
    '''
    return json.dumps(db.Thread.get(thread_id))


@app.route('/thread/', methods=['POST'])
def create_thread():
    ''' create_thread -> POST /thread/
    Creates a thread for the forum
    '''
    title = request.form['title']
    content = request.form['content']
    db.Thread.create({
        "title": title,
        "content": content,
        "user": session['id'],
        "datetime": datetime.datetime.utcnow()
    })
    return "", httplib.CREATED


@app.route('/thread/<thread_id>', methods=['PUT'])
def edit_thread(thread_id):
    ''' edit_thread -> PUT /thread/<thread_id>
    If the user is the one who created the thread, will save edits to the
    thread details, otherwise tosses an error
    '''
    title = request.form['title']
    try:
        db.Thread.edit_thread(thread_id, session['id'], {
            "title": title,
            "datetime": datetime.datetime.utcnow()
        })
    except db_errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return "", httplib.ACCEPTED


@app.route('/post/<post_id>', methods=['PUT'])
def edit_post(post_id):
    ''' edit_post -> PUT /post/<post_id>
    '''
    content = request.form['content']
    try:
        db.Thread.edit_post(post_id, session['id'], {
            "content": content,
            "datetime": datetime.datetime.utcnow()
        })
    except db_errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return "", httplib.ACCEPTED


@app.route('/post/<post_id>', methods=['GET'])
def view_post(post_id):
    ''' view_post -> GET /post/<post_id>
    '''
    return json.dumps(db.Thread.get_post(post_id))


@app.route('/thread/<thread_id>', methods=['POST'])
def replyto_thread(thread_id):
    ''' replyto_thread -> POST /thread/<thread_id>
    Replies to the thread, creates another post in the thread
    '''
    content = request.form['content']
    db.Thread.reply(thread_id, {
        "content": content,
        "user": session["id"],
        "datetime": datetime.datetime.utcnow()
    })
    return "", httplib.CREATED

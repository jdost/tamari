import json
import httplib
import datetime
from tamari import app
from db import connect

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


@app.route('/thread/', methods=['PUT'])
def create_thread():
    ''' create_thread -> PUT /thread/
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
def replyto_thread(thread_id):
    ''' replyto_thread -> PUT /thread/<thread_id>
    Replies to the thread, creates another post in the thread
    '''
    content = request.form['content']
    db.Thread.reply(thread_id, {
        "content": content,
        "user": session["id"],
        "datetime": datetime.datetime.utcnow()
    })
    return "", httplib.CREATED

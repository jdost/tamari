import httplib
import datetime
from . import app
from .decorators import datatype, require_permissions, paginate
from .database import Forum, Thread
from flask import request, session


@app.get('/forum/<forum_id>')
@datatype
def get_forum(forum_id, page=0, per_page=25):
    return Forum.get(forum_id)


@app.get('/forum/<forum_id>/thread')
@paginate
@datatype
def get_threads(forum_id, page=0, per_page=25):
    ''' get_threads -> GET /forum/<forum_id>/thread
    gets a list of the threads for a specific forum
    '''
    return Thread.get(
        forum=forum_id, limit=per_page, start=(page * per_page))


@app.post('/forum/<forum_id>/thread')
@datatype
def create_thread(forum_id):
    ''' create_thread -> POST /forum/<forum_id>/thread
    Creates a thread for the forum
    '''
    title = request.form['title']
    content = request.form['content']
    thread = Thread.create({
        "title": title,
        "content": content,
        "user": session['id'],
        "created": datetime.datetime.utcnow(),
        "forum": forum_id
    })
    return thread, httplib.CREATED


@app.get('/forum/<forum_id>/forum')
@datatype
def get_forums(forum_id):
    ''' get_forums -> GET /forum/<forum_id>/forum
    gets a list of the subforums for a specified forum
    '''
    return Forum.children(parent=forum_id)


@app.post('/forum/<forum_id>/forum')
@datatype
@require_permissions(forum=True)
def create_forum(forum_id):
    packet = request.json if request.json else {"name": request.form['name']}
    packet['parent'] = forum_id

    return Forum.create(packet), httplib.CREATED

# Creates the initial root forum if it doesn't exist
#root_url = url_for('get_forums', forum_id=str(Forum.get_root()))
app.endpoint('root', '/forum/' + str(Forum.get_root()))

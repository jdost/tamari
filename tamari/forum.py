import httplib
import datetime
from . import app
from .decorators import datatype, require_permissions, paginate
from .database import Forum, Thread, errors
from flask import request, session

forum_base = '/forum/<forum_id>'
forum_route = forum_base + '/forum'
thread_route = forum_base + '/thread'


@app.get(forum_base)
@datatype
def get_forum(forum_id, page=0, per_page=25):
    ''' get_forum -> GET /forum/<forum_id>

    Retrieves the base listing for the specified forum (specified by the route
    arg of <forum_id>).  This will return the basic information for the forum,
    including the URLs to retrieve the list of subforums and the list of
    threads.  Returns a NOT_FOUND if the <forum_id> fails to find a
    corresponding forum.
    '''
    try:
        forum = Forum.get(forum_id)
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return forum if isinstance(forum, dict) else httplib.NOT_FOUND


@app.get(thread_route)
@paginate
@datatype
def get_threads(forum_id, page=0, per_page=25):
    ''' get_threads -> GET /forum/<forum_id>/thread

    Retrieves a paged list of threads for the specified forum (specified by
    the route arg of <forum_id>).  The result will be paged based on the format
    dictated by the paginate decorator.  The threads in the list will be a
    summary packet for each, with the majority of information coming from the
    URL provided by each packet.  Returns a NOT_FOUND if the <forum_id> fails
    to find results.
    '''
    try:
        threads = Thread.get(
            forum=forum_id, limit=per_page, start=(page * per_page))
    except errors.NoEntryFound as err:
        return str(err), httplib.NOT_FOUND
    return threads if isinstance(threads, list) else httplib.NOT_FOUND


@app.post(thread_route)
@datatype
@require_permissions
def create_thread(forum_id):
    ''' create_thread -> POST /forum/<forum_id>/thread
        POST: title=[string]&content=[string]

    Tries to create a thread for the forum specified by the <forum_id> route
    arg.  Expects for both 'title' and 'content' to be provided in the POST
    header.  Uses these to try and create the thread using the current session
    as the creating user.  Will return a BAD_REQUEST if the request is lacking
    required information and a NOT_FOUND if the <forum_id> does not correspond
    to an existing forum in the database, otherwise returns CREATED and the
    new thread structure.
    '''
    if 'title' not in request.form and 'content' not in request.form:
        return httplib.BAD_REQUEST

    title = request.form['title']
    content = request.form['content']
    try:
        thread = Thread.create({
            "title": title,
            "content": content,
            "user": session['id'],
            "created": datetime.datetime.utcnow(),
            "forum": forum_id
        })
    except errors.MissingInfoError as err:
        return str(err), httplib.BAD_REQUEST
    except errors.NoEntryFound as err:
        return str(err), httplib.NOT_FOUND
    return thread, httplib.CREATED


@app.get(forum_route)
@datatype
def get_forums(forum_id):
    ''' get_forums -> GET /forum/<forum_id>/forum

    Retrieves a list of forums that are children of the specified forum
    (specified by the <forum_id> route arg).  These are not currently
    paginated.  If the forum_id fails to find a corresponding forum, a
    NOT_FOUND will be returned otherwise will be the list of subforums.
    '''
    try:
        forums = Forum.children(parent=forum_id)
    except errors.NoEntryFound as err:
        return str(err), httplib.NOT_FOUND
    return forums if isinstance(forums, list) else httplib.NOT_FOUND


@app.post(forum_route)
@datatype
@require_permissions(forum=True)
def create_forum(forum_id):
    ''' create_forum -> POST /forum/<forum_id>
        POST: name=[string]

    Tries to create a forum using the provided information.  Requires the
    current user to have permissions on the forum specified by <forum_id>.  The
    new forum will be a sub forum of this forum.  If the creation succeeds, a
    CREATED will be returned with the new forum's information.  If there is
    information missing, a BAD_REQUEST will be returned, if the <forum_id>
    does not correspond to a forum in the system.
    '''
    if not request.json and "name" not in request.form:
        return httplib.BAD_REQUEST

    packet = request.json if request.json else {"name": request.form['name']}
    packet['parent'] = forum_id

    try:
        forum = Forum.create(packet)
    except errors.NoEntryFound as err:
        return str(err), httplib.NOT_FOUND
    except errors.MissingInfoError as err:
        return str(err), httplib.BAD_REQUEST

    return (forum, httplib.CREATED) if forum else httplib.NOT_FOUND

# Creates the initial root forum if it doesn't exist
app.endpoint('root', '/forum/' + str(Forum.get_root()))

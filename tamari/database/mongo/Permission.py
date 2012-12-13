from . import database as mongo
from . import settings, ObjectId
from .Forum import find_parent
from flask import session

forums = mongo.forums
threads = mongo.threads
posts = mongo.posts

inherit = settings.INHERIT_ADMINS


def is_admin():
    return 0 in session['rights']


def check_forum(forum_id):
    if is_admin():
        return True
    return find_parent(forum_id, session['rights']) if inherit \
        else forum_id in session['rights']


def check_thread(thread_id):
    thread = threads.find_one({'_id': ObjectId(thread_id)})
    return True if str(thread['user']) == session['id'] \
        else check_forum(str(thread['forum']))


def check_post(post_id):
    post = posts.find_one({'_id': ObjectId(post_id)})
    if str(post['user']) != session['id']:
        thread = threads.find_one({'_id': post['thread']})
        return check_forum(str(thread['forum']))
    return True

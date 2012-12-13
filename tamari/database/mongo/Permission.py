''' Permissions.py
Permissions checking is established in here per database backend, this will
provide functions that deal with checking permissions on whether a user has
permissions to modify and create and specific levels based on their rights and
the settings of the application.
'''
from . import database as mongo
from . import settings, ObjectId
from .Forum import find_parent
from flask import session

forums = mongo.forums
threads = mongo.threads
posts = mongo.posts

inherit = settings.INHERIT_ADMINS


def is_root():
    ''' is_root
    Returns whether the user is the root user, giving them super rights across
    the application.
    '''
    return 0 in session['rights']


def check_forum(forum_id):
    ''' check_forum
    Returns whether the user has the rights to modify things in the specified
    forum level.  This will check parents if the application property
    INHERIT_ADMINS is set (i.e. an admin at the root level has rights to modify
    the root > sub_forum level)
    '''
    if is_root():
        return True
    return find_parent(forum_id, session['rights']) if inherit \
        else forum_id in session['rights']


def check_thread(thread_id):
    ''' check_thread
    Returns whether the user has the rights to modify the specified forum.
    If the user is the creator of the thread, they have rights, if the user is
    an admin of the forum posted in, they have rights.
    '''
    thread = threads.find_one({'_id': ObjectId(thread_id)})
    return True if str(thread['user']) == session['id'] \
        else check_forum(str(thread['forum']))


def check_post(post_id):
    ''' check_post
    Returns whether the user has the rights to modify the specified post.  If
    the user is the creator of the post, they have rights, if the user is an
    admin of the forum posted in, they have rights.
    '''
    post = posts.find_one({'_id': ObjectId(post_id)})
    if str(post['user']) != session['id']:
        thread = threads.find_one({'_id': post['thread']})
        return check_forum(str(thread['forum']))
    return True

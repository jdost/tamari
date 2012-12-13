''' Thread
The wrapper class for operations on threads in the database backend, there
are two tables, one is a table of threads, this will hold the title (which
is not going to be part of each post) and the head post, then there is a
much larger table of posts which all belong to a thread
'''
from . import database as mongo
from . import clean_dict, ObjectId, convert_id
from .. import errors
from datetime import datetime
from pymongo import DESCENDING, ASCENDING
from flask import url_for, session

threads = mongo.threads
thread_keys = ["title", "user", "head", "created", "_id", "editted",
               "forum"]
posts = mongo.posts
post_keys = ["content", "user", "thread", "created", "_id", "editted"]


def create(info=None):
    ''' create
    Single argument function, this argument should be the thread being
    created.  The keys for the thread will be pulled out and stored in as
    thread with a pointer to the post information as the 'head' of the
    thread, then the rest will be stored as a post beginning the thread.
    '''
    if not info:
        raise errors.MissingInfoError('No thread information provided')

    info.update({
        "created": datetime.utcnow(),
        "editted": None
    })
    # Convert IDs into ObjectIds
    info['user'] = ObjectId(info['user'])  # Convert id into ObjectId
    if 'forum' in info:
        info['forum'] = ObjectId(info['forum'])
    # Create placeholder for initial post in thread
    post = clean_dict(info, post_keys)
    post_id = posts.insert({"temp": ""})  # placeholder
    post["_id"] = post_id
    info['head'] = post_id
    # Create thread
    thread_id = threads.insert(clean_dict(info, thread_keys))
    # Create initial post properly
    post["thread"] = thread_id
    posts.save(post)

    return get(thread_id=thread_id)


def edit_thread(id, user=None, info=None):
    ''' edit_thread
    Modifies the thread entry in the database based on the thread id that
    is passed in.  First checks that the user id provided is the same as
    the user that created the thread, if it is not, raises an error,
    otherwise the thread will be updated with the provided information.
    '''
    if not info:
        raise errors.MissingInfoError('No thread information provided')

    user = user if user else session['id']
    info.update({
        "editted": datetime.utcnow(),
        "editted_by": ObjectId(user)
    })
    # Retrieve thread to be changed
    thread = threads.find_one({"_id": ObjectId(id)})
    if not thread:
        raise errors.NoEntryError('No thread found for provided id')
    # Update thread object with new information & save
    thread.update(info)
    id = threads.save(thread)

    return get(thread_id=id)


def get(thread_id=None, forum=None, limit=0, start=0):
    ''' get
    Retrieval function for threads.  The purpose is to return all of the
    threads based on given conditions.  If the id argument is set, it will
    return more granular information on that single thread, if it is not,
    a list of threads with a simple summary will be returned instead.
    '''
    if not thread_id:  # Thread list
        thread_set = threads.find(
            {"forum": ObjectId(forum)}, skip=start, limit=limit,
            sort=[("created", DESCENDING)])
        return [__short(thread) for thread in thread_set]
    else:  # Single thread
        thread_id = ObjectId(thread_id)
        thread = threads.find_one({"_id": thread_id})
        if not thread:
            raise errors.NoEntryError('No thread found for provided id')
        post_set = posts.find(
            {"thread": thread_id}, skip=start, limit=limit,
            sort=[("created", ASCENDING)])
        return __full(thread, post_set)


def get_post(id=None):
    ''' get_post
    Retrieval function to get a single post.  Just requires the identifier
    for the desired post and will return the entry in the database.  If
    the identifier is not found or provided, an error will be raised.
    '''
    if not id:
        raise errors.MissingInfoError("No id provided to retrieve post for")
    # Retrieve post
    post = posts.find_one({"_id": ObjectId(id)})
    if not post:
        raise errors.NoEntryError("No post found for provided id")

    return __post(post)


def reply(id=None, post=None):
    ''' reply
    Creates a post in reply to a thread, this does not create a new thread
    but instead adds onto an existing thread, there are two arguments, the
    id of the thread being replied to and the actual post that is a reply
    to the thread
    '''
    if not id or not post:
        raise errors.MissingInfoError('No id/post provided for the reply')
    post.update({
        'user': ObjectId(post['user']),
        "thread": ObjectId(id)
    })
    return get_post(posts.save(clean_dict(post, post_keys)))


def edit_post(id, user=None, info=None):
    ''' edit_post
    Modifies the post entry in the databased based on the post id that is
    passed in.  First checks that the passed in user id is the same as the
    one attached to the post itself, otherwise raises an error.
    '''
    if not info:
        raise errors.MissingInfoError('No post information provided')

    user = user if user else session['id']
    info.update({
        "editted": datetime.utcnow(),
        "editted_by": ObjectId(user)
    })
    # Retrieve the post to be changed
    post = posts.find_one({"_id": ObjectId(id)})
    if not post:
        raise errors.NoEntryError('No post found for provided id')
    # Update post object with new information & save
    post.update(info)
    id = posts.save(post)

    return get_post(id=id)


def __short(thread):
    ''' (private) __short
    Summarizes a thread entry from the database
    '''
    return {
        "url": url_for("get_thread", thread_id=str(thread['_id'])),
        "title": thread["title"],
        "created": thread["created"],
        "user": str(thread["user"])
    }


def __full(thread, posts):
    ''' (private) _full
    Cleans up the full document from the database
    '''
    convert_id(thread)
    thread['url'] = url_for("get_thread", thread_id=thread['id'])
    thread['posts'] = [__post(post) for post in posts]
    return thread


def __post(post):
    ''' (private) __post
    Cleans up the full document from the database
    '''
    convert_id(post)
    post['url'] = url_for("get_post", post_id=post['id'])
    return post

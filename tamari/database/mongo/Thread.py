''' Thread
The wrapper class for operations on threads in the database backend, there
are two tables, one is a table of threads, this will hold the title (which
is not going to be part of each post) and the head post, then there is a
much larger table of posts which all belong to a thread
'''
from . import database as mongo
from . import check_permissions, clean_dict, ObjectId
from .. import errors
from pymongo import DESCENDING, ASCENDING
from flask import url_for
threads = mongo.threads
thread_keys = ["title", "user", "head", "created", "_id", "editted",
               "forum"]
posts = mongo.posts
post_keys = ["content", "user", "thread", "created", "_id", "editted"]


def create(info=None):
    ''' Thread::create
    Single argument function, this argument should be the thread being
    created.  The keys for the thread will be pulled out and stored in as
    thread with a pointer to the post information as the 'head' of the
    thread, then the rest will be stored as a post beginning the thread.
    '''
    if not info:
        raise errors.MissingInfoError('No thread information provided')

    info['user'] = ObjectId(info['user'])  # Convert id into ObjectId
    if 'forum' in info:
        info['forum'] = ObjectId(info['forum'])

    post_id = posts.insert({"temp": ""})  # placeholder
    info['head'] = post_id
    thread_id = threads.insert(clean_dict(info, thread_keys))

    post = clean_dict(info, post_keys)
    post["thread"] = thread_id
    post["_id"] = post_id
    posts.save(post)
    return get(thread_id=thread_id)


def edit_thread(id, user, info):
    ''' Thread::edit_thread
    Modifies the thread entry in the database based on the thread id that
    is passed in.  First checks that the user id provided is the same as
    the user that created the thread, if it is not, raises an error,
    otherwise the thread will be updated with the provided information.
    '''
    id = ObjectId(id)
    thread = threads.find_one({"_id": id})
    if not check_permissions(thread, user):
        raise errors.BadPermissionsError()
    thread.update(info)
    threads.save(clean_dict(thread, thread_keys))
    return id


def get(thread_id=None, forum=None, limit=0, start=0):
    ''' Thread::get
    Retrieval function for threads.  The purpose is to return all of the
    threads based on given conditions.  If the id argument is set, it will
    return more granular information on that single thread, if it is not,
    a list of threads with a simple summary will be returned instead.
    '''
    if not thread_id:
        forum = ObjectId(forum) if forum else forum
        thread_set = threads.find(
            {"forum": forum}, skip=start,
            limit=limit, sort=[("created", DESCENDING)])
        return [__short(thread) for thread in thread_set]
    else:
        thread_id = ObjectId(thread_id)
        thread = threads.find_one({"_id": thread_id})
        if not thread:
            raise errors.IncorrectIdError()
        post_set = posts.find(
            {"thread": thread_id}, skip=start, limit=limit,
            sort=[("created", ASCENDING)])
        return __full(thread, post_set)


def get_post(id=None):
    ''' Thread::get_post
    Retrieval function to get a single post.  Just requires the identifier
    for the desired post and will return the entry in the database.  If
    the identifier is not found or provided, an error will be raised.
    '''
    if not id:
        raise errors.MissingInfoError()
    id = ObjectId(id)
    post = posts.find_one({"_id": id})
    if not post:
        raise errors.IncorrectIdError()
    return __post(post)


def reply(id=None, post=None):
    ''' Thread::reply
    Creates a post in reply to a thread, this does not create a new thread
    but instead adds onto an existing thread, there are two arguments, the
    id of the thread being replied to and the actual post that is a reply
    to the thread
    '''
    if not id or not post:
        raise errors.MissingInfoError(
            'No id/post provided for the reply')
    post['user'] = ObjectId(post['user'])
    post = clean_dict(post, post_keys)
    post["thread"] = ObjectId(id)
    return posts.save(post)


def edit_post(id, user, info):
    ''' Thread::edit_post
    Modifies the post entry in the databased based on the post id that is
    passed in.  First checks that the passed in user id is the same as the
    one attached to the post itself, otherwise raises an error.
    '''
    id = ObjectId(id)
    post = posts.find_one({"_id": id})
    if not check_permissions(post, user):
        raise errors.BadPermissionsError()
    post.update(info)
    return posts.save(clean_dict(post, post_keys))


def __short(thread):
    ''' (private) ::__short
    Summarizes a thread entry from the database
    '''
    return {
        "url": url_for("get_thread", thread_id=str(thread['_id'])),
        "title": thread["title"],
        "created": thread["created"],
        "user": str(thread["user"])
    }


def __full(thread, posts):
    ''' (private) ::_full
    '''
    return {
        "url": url_for("get_thread", thread_id=str(thread['_id'])),
        "title": thread["title"],
        "user": str(thread["user"]),
        "created": thread["created"],
        "editted": thread.get("editted", None),
        "forum": thread['forum'],
        "posts": [__post(post) for post in posts]
    }


def __post(post):
    ''' (private) ::__post
    '''
    return {
        "url": url_for("get_post", post_id=str(post['_id'])),
        "content": post["content"],
        "created": post["created"],
        "editted": post.get("editted", None),
        "user": str(post["user"])
    }

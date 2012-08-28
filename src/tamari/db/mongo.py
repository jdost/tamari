import pymongo as mongo
import db_errors
from tamari.settings import settings
from bson.objectid import ObjectId

# Default properties
db_info = {
    'host': 'localhost',
    'port': 27017
}
db_info.update(settings['db'])  # This overrides the defaults with the ones in
        # settings
connection = mongo.Connection(db_info['host'], db_info['port'])
if settings["debug"]:
    database = connection.test_database
else:
    database = connection.prod_database


def cleanup():
    if settings["debug"]:
        connection.drop_database("test_database")


def clean_dict(src, keys):
    dst = {}
    for key in keys:
        if key in src.keys():
            dst[key] = src[key]
    return dst


def check_permissions(src, user):
    if str(src["user"]) != user["id"]:
        check = src
        if "thread" in check:  # means it is a post (?)
            check = database.threads.find_one({"_id": check["thread"]})
        if "forum" in check:  # means it is a thread
            check = database.forums.find_one({"_id": check["forum"]})
        if str(check["_id"]) in user["permissions"]:  # check if forum admin
            return True

        while "parent" in check:  # check if admin of any parent forum
            if str(check["parent"] in user["permissions"]):
                return True
            check = database.forums.find_one({"_id": check["parent"]})

        return 0 in user["permissions"] or 1 in user["permissions"]
                # root or admin permissions
    return True


class Thread:
    ''' Thread
    The wrapper class for operations on threads in the database backend, there
    are two tables, one is a table of threads, this will hold the title (which
    is not going to be part of each post) and the head post, then there is a
    much larger table of posts which all belong to a thread
    '''
    threads = database.threads
    thread_keys = ["title", "user", "head", "created", "_id", "editted",
            "forum"]
    posts = database.posts
    post_keys = ["content", "user", "thread", "created", "_id", "editted"]

    @classmethod
    def create(cls, info=None):
        ''' Thread::create
        Single argument function, this argument should be the thread being
        created.  The keys for the thread will be pulled out and stored in as
        thread with a pointer to the post information as the 'head' of the
        thread, then the rest will be stored as a post beginning the thread.
        '''
        if not info:
            raise db_errors.MissingInfoError('No thread information provided')

        info['user'] = ObjectId(info['user'])  # Convert id into ObjectId

        post_id = cls.posts.insert({"temp": ""})  # placeholder
        info['head'] = post_id
        thread_id = cls.threads.insert(clean_dict(info, cls.thread_keys))

        post = clean_dict(info, cls.post_keys)
        post["thread"] = thread_id
        post["_id"] = post_id
        cls.posts.save(post)
        return thread_id

    @classmethod
    def edit_thread(cls, id, user, info):
        ''' Thread::edit_thread
        Modifies the thread entry in the database based on the thread id that
        is passed in.  First checks that the user id provided is the same as
        the user that created the thread, if it is not, raises an error,
        otherwise the thread will be updated with the provided information.
        '''
        id = ObjectId(id)
        thread = cls.threads.find_one({"_id": id})
        if not check_permissions(thread, user):
            raise db_errors.BadPermissionsError()
        thread.update(info)
        cls.threads.save(clean_dict(thread, cls.thread_keys))
        return id

    @classmethod
    def get(cls, id=None, limit=0, start=0):
        ''' Thread::get
        Retrieval function for threads.  The purpose is to return all of the
        threads based on given conditions.  If the id argument is set, it will
        return more granular information on that single thread, if it is not,
        a list of threads with a simple summary will be returned instead.
        '''
        if not id:
            threads = cls.threads.find(skip=start, limit=limit,
                    sort=[("created", mongo.DESCENDING)])
            return [cls.__short(thread) for thread in threads]
        else:
            id = ObjectId(id)
            thread = cls.threads.find_one({"_id": id})
            if not thread:
                raise db_errors.IncorrectIdError()
            posts = cls.posts.find({"thread": id}, skip=start, limit=limit,
                    sort=[("created", mongo.ASCENDING)])
            return cls.__full(thread, posts)

    @classmethod
    def get_post(cls, id=None):
        ''' Thread::get_post
        Retrieval function to get a single post.  Just requires the identifier
        for the desired post and will return the entry in the database.  If the
        identifier is not found or provided, an error will be raised.
        '''
        if not id:
            raise db_errors.MissingInfoError()
        id = ObjectId(id)
        post = cls.posts.find_one({"_id": id})
        if not post:
            raise db_errors.IncorrectIdError()
        return cls.__post(post)

    @classmethod
    def reply(cls, id=None, post=None):
        ''' Thread::reply
        Creates a post in reply to a thread, this does not create a new thread
        but instead adds onto an existing thread, there are two arguments, the
        id of the thread being replied to and the actual post that is a reply
        to the thread
        '''
        if not id or not post:
            raise db_errors.MissingInfoError('No id/post provided ' +
                    'for the reply')
        post['user'] = ObjectId(post['user'])
        post = clean_dict(post, cls.post_keys)
        post["thread"] = ObjectId(id)
        return cls.posts.save(post)

    @classmethod
    def edit_post(cls, id, user, info):
        ''' Thread::edit_post
        Modifies the post entry in the databased based on the post id that is
        passed in.  First checks that the passed in user id is the same as the
        one attached to the post itself, otherwise raises an error.
        '''
        id = ObjectId(id)
        post = cls.posts.find_one({"_id": id})
        if not check_permissions(post, user):
            raise db_errors.BadPermissionsError()
        post.update(info)
        return cls.posts.save(clean_dict(post, cls.post_keys))

    @classmethod
    def __short(cls, thread):
        ''' (private) ::__short
        Summarizes a thread entry from the database
        '''
        return {
            "id": str(thread["_id"]),
            "title": thread["title"],
            "created": thread["created"],
            "user": str(thread["user"])
        }

    @classmethod
    def __full(cls, thread, posts):
        ''' (private) ::_full
        '''
        return {
            "id": str(thread["_id"]),
            "title": thread["title"],
            "user": str(thread["user"]),
            "created": thread["created"],
            "editted": thread.get("editted", None),
            "posts": [cls.__post(post) for post in posts]
        }

    @classmethod
    def __post(cls, post):
        ''' (private) ::__post
        '''
        return {
            "id": str(post["_id"]),
            "content": post["content"],
            "created": post["created"],
            "editted": post.get("editted", None),
            "user": str(post["user"])
        }


class User:
    ''' User
    The wrapper class for operations on users in the database backend, this
    includes things like creating a new user, logging in as a user, or getting
    the public information of a user.
    '''
    db = database.users
    user_keys = ["username", "password"]

    @classmethod
    def create(cls, info=None):
        ''' User::create
        Single argument function, this argument should be a dictionary of all
        of the information for this user.  At this point, there should be
        minimal validation on this packet and it will really just be inserted
        into the DB as is.
        '''
        if cls.db.find_one({"username": info["username"]}):
            raise db_errors.ExistingUsernameError('Username already exists')
        if not info:
            raise db_errors.MissingInfoError('No info packet provided')
        return cls.db.insert(clean_dict(info, cls.user_keys))

    @classmethod
    def login(cls, username, password):
        ''' User::login
        Performs a login check with the provided credentials, the password is
        just looking for a match, the hashing occurs above the layer.  Returns
        None if no matching user was found.
        '''
        user = cls.db.find_one({"username": username, "password": password})
        if user:
            return cls.__private(user), user['_id']
        return None, None

    @classmethod
    def get(cls, id=None, private=False):
        ''' User::get
        Returns the public form of the user with the provided ID, if no ID is
        provided, throws an error.  If no user is found with the ID, returns
        None
        '''
        if not id:
            raise db_errors.MissingInfoError('No ID for the user request')
        user = cls.db.find_one({"_id": ObjectId(id)})
        if user:
            return cls.__public(user) if not private else cls.__private(user)
        return None

    @classmethod
    def delete(cls, id=None):
        ''' User::delete
        '''
        if not id:
            raise db_errors.MissingInfoError('No ID for the user deletion')
        cls.db.remove(ObjectId(id))

    @classmethod
    def __private(cls, user):
        ''' (private) ::__private
        method for formatting the information when used *by* the user (this
        is all of the private information for the user).  This method is used
        to standardize the output format from the DB wrapper to the API layer.
        '''
        return {
            'username': user['username'],
            'id': str(user['_id'])
        }

    @classmethod
    def __public(cls, user):
        ''' (private) ::__public
        method for formatting the information when used by another user (this
        is for all of the public information for the user).  This method is
        used to standardize the output format from the DB wrapper to the API
        layer.
        '''
        return {
            'username': user['username']
        }


class Session:
    db = database.sessions

    @classmethod
    def get(cls, id):
        return cls.db.find_one({"_id": ObjectId(id)})

    @classmethod
    def save(cls, packet):
        return cls.db.save(packet, safe=True)

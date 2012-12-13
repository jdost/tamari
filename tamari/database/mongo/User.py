''' User
The wrapper class for operations on users in the database backend, this
includes things like creating a new user, logging in as a user, or getting
the public information of a user.
'''
from . import database as mongo
from . import convert_id, ObjectId
from .. import errors
from flask import url_for
from datetime import datetime
database = mongo.users
user_keys = ["username", "password"]


def create(info):
    ''' create
    Single argument function, this argument should be a dictionary of all
    of the information for this user.  At this point, there should be
    minimal validation on this packet and it will really just be inserted
    into the DB as is.
    '''
    if database.find_one({"username": info["username"]}):
        raise errors.ExistingUsernameError(
            "Username: {} already exists", info["username"])

    if 'rights' not in info:
        info['rights'] = []

    if database.count() == 0:
        info['rights'].append(0)

    info.update({
        'created': datetime.utcnow(),
        'modified': None,
        'modified_by': None
    })

    id = database.insert(info)

    return str(id), __private(info)


def login(username, password):
    ''' login
    Performs a login check with the provided credentials, the password is
    just looking for a match, the hashing occurs above the layer.  Returns
    None if no matching user was found.
    '''
    user = database.find_one({"username": username, "password": password})
    if user:
        return user['_id'], __private(user)
    return None, None


def get(id=None, private=False):
    ''' get
    Returns the public form of the user with the provided ID, if no ID is
    provided, throws an error.  If no user is found with the ID, returns
    None
    '''
    if not id:
        raise errors.MissingInfoError('No ID for the user request')

    user = database.find_one({"_id": ObjectId(id)})
    if not user:
        raise errors.NoEntryError("No user found with the provided id")
    return __public(user) if not private else __private(user)


def delete(id=None):
    ''' delete
    Removes the specified user from the database.  If no ID is provided or the
    ID does not point to an existing user, an error is raised.
    '''
    if not id:
        raise errors.MissingInfoError('No ID for the user deletion')
    database.remove(ObjectId(id))


def __private(user):
    ''' (private) __private
    method for formatting the information when used *by* the user (this
    is all of the private information for the user).  This method is used
    to standardize the output format from the DB wrapper to the API layer.
    '''
    private_packet = user.copy()
    convert_id(private_packet)
    del private_packet["password"]

    private_packet['url'] = url_for('get_user', user_id=private_packet['id'])

    return private_packet


def __public(user):
    ''' (private) __public
    method for formatting the information when used by another user (this
    is for all of the public information for the user).  This method is
    used to standardize the output format from the DB wrapper to the API
    layer.
    '''
    return {
        'username': user['username'],
        'url': url_for('get_user', user_id=str(user['_id']))
    }

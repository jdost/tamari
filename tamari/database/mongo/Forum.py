''' Forum
The wrapper class for operations on forums in the database backend, this
includes things like creating a forum, getting the list of forums at
different levels of the hierarchy
'''
from . import database as mongo
from . import convert_id, ObjectId
from .. import errors
from flask import url_for
database = mongo.forums


def create(info):
    ''' Forum::create
    Single argument function, this argument should be a dictionary of all
    of the information for creating this forum.  Should really just have
    a name and a parent, if it's parent is root, don't add it
    '''
    if not info:
        raise errors.MissingInfoError('No forum information provided')

    if info['parent']:
        info['parent'] = ObjectId(info['parent'])

    return get(database.insert(info))


def get(forum_id):
    ''' Forum::get
    Returns the forum information for the specified forum level, the level
    should be the ID of the forum, if level is not specified, it will
    return a list of the root subforums
    '''
    return __full(database.find_one({'_id': ObjectId(forum_id)}))


def children(parent=None):
    parent = ObjectId(parent)
    return [__simple(forum) for forum in database.find({'parent': parent})]


def get_root():
    ''' Forum::get_root
    '''
    if database.count() == 0:
        return database.insert({
            'name': 'root',
            'parent': None
        })
    else:
        return database.find_one({'parent': None})['_id']


def __simple(forum):
    return {
        "url": url_for('get_forum', forum_id=str(forum['_id'])),
        "name": forum['name']
    }


def __full(packet):
    forum = packet.copy()
    convert_id(forum)
    forum['url'] = url_for('get_forum', forum_id=forum['id'])
    forum['threads'] = url_for('get_threads', forum_id=forum['id'])
    forum['forums'] = url_for('get_forums', forum_id=forum['id'])
    return forum


def find_parent(forum, id_list):
    if 0 in id_list or 1 in id_list:
        return True

    forum = database.find_one({'_id': ObjectId(forum)})
    while forum['parent']:
        if str(forum['_id']) in id_list:
            return True

        forum = database.find_one({'_id': forum['parent']})

    return str(forum['_id']) in id_list

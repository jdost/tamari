import pymongo as mongo
from bson.objectid import ObjectId as ObjectId_
from bson.errors import InvalidId
from .. import errors
from sys import modules
settings = modules['tamari.settings']

# Default properties
connection_info = {
    'host': 'localhost',
    'port': 27017
}
connection_info.update(settings.DATABASE['info'])  # This overrides the
    # defaults with the ones in settings
connection = mongo.Connection(**connection_info)

database = connection["tamari_dev" if settings.DEBUG else "tamari"]


def cleanup():
    if settings.DEBUG:
        connection.drop_database("tamari_dev")


def clean_dict(src, keys):
    dst = {}
    for key in keys:
        if key in src.keys():
            dst[key] = src[key]
    return dst


def __getattr__(key):
    return __dict__[key] if key in __dict__ else database[key]


def check_permissions(src, user):
    if "user" in src and str(src["user"]) == user["id"]:
        return True

    if "thread" in src:
        src = database.threads.find_one({"_id": src["thread"]})
    if "forum" in src:
        src = database.forums.find_one({"_id": src["forum"]})

    if src and "_id" in src and str(src["_id"]) in user["permissions"]:
        return True
    while src and "parent" in src:
        if str(src["parent"]) in user["permissions"]:
            return True
        src = database.forums.find_one({"_id": src["parent"]})
    return 0 in user["permissions"] or 1 in user["permissions"]
            # root or admin permissions


def ObjectId(src):
    try:
        return ObjectId_(src)
    except InvalidId:
        raise errors.NoEntryError(
            "Information provided to find a document used an ID not from " +
            "the system.")


def convert_id(packet):
    packet["id"] = str(packet["_id"])
    del packet["_id"]

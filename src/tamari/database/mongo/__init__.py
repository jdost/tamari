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
    ''' cleanup
    Used by the unittest system to cleanup the database between tests
    '''
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


def ObjectId(src):
    ''' ObjectId
    Wraps the conversion of a provided string into a BSON ObjectId, handles
    if the conversion fails and throws an error, bubbling it up to a
    NoEntryError.
    '''
    try:
        return ObjectId_(src)
    except InvalidId:
        raise errors.NoEntryError(
            "Information provided to find a document used an ID not from " +
            "the system.")


def convert_id(packet):
    ''' convert_id
    Helper function that converts a packet's _id property used in Mongo into
    an identifying string for the application.
    '''
    packet["id"] = str(packet["_id"])
    del packet["_id"]

    for (key, value) in packet.items():
        if isinstance(value, ObjectId_):
            packet[key] = str(value)

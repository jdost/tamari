from . import database as mongo
from bson.objectid import ObjectId
database = mongo.sessions


def get(id):
    return database.find_one({"_id": ObjectId(id)})


def save(packet):
    return database.save(packet, safe=True)


def remove(id):
    return database.remove(ObjectId(id))

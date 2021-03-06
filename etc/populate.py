#!/bin/env python2

from tamari import app, cleanup
from tamari.database import User, Forum, Thread

cleanup()

users = [
    {"username": "admin", "password": "admin"},
    {"username": "user", "password": "user"},
]

root = Forum.get_root()
forums = [
    {"name": "subforum", "parent": root},
]

threads = [
]

app.config['SERVER_NAME'] = 'localhost'
with app.app_context():
    map(User.create, users)

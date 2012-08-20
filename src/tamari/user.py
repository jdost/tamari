from db import connect
from db import db_errors
import json
import httplib
from tamari import pwhash, app

db = connect()
from flask import request, session, abort


@app.route('/user', methods=['PUT'])
def login():
    ''' login -> PUT /user/
    attempts a login with the provided information, if successful, stores the
    user's id in the session and returns the user information
    '''
    username = request.form['username']
    password = request.form['password']
    info, id = db.User.login(username, pwhash(password))
    if id:
        session['id'] = str(id)
        return json.dumps(info), httplib.ACCEPTED
    else:
        return str(id), httplib.BAD_REQUEST


@app.route('/logout', methods=['GET'])
def logout():
    ''' logout -> GET /logout
    will delete the id reference for the user in the session, effectively
    logging the user out.
    '''
    session.pop('id', None)
    return "", httplib.ACCEPTED


@app.route('/user', methods=['POST'])
def register():
    ''' register -> POST /user/
    attempts to create/'register' a new user with the provided information,
    will return a CONFLICT error if the username already is registered.  If
    successful, the user id is stored in the session, logging in the user
    '''
    username = request.form['username']
    password = request.form['password']
    try:
        id = db.User.create({
            'username': username,
            'password': pwhash(password)
        })
    except db_errors.ExistingUsernameError:
        return "", httplib.CONFLICT
    session['id'] = str(id)
    return str(id), httplib.CREATED


@app.route('/user', methods=['DELETE'])
def delete_user():
    ''' delete_user -> DELETE /user/
    will try to delete the user's entry from the database and then log the user
    out
    '''
    if 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    db.User.delete(session['id'])
    session.pop('id', None)
    return "", httplib.ACCEPTED


@app.route('/user', methods=['GET'])
def show_current():
    ''' show_current -> GET /user/
    simple retrieval of the user information at any time, same information
    that gets returned on a login
    '''
    if 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    info = db.User.get(session["id"], True)
    return json.dumps(info)


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    ''' get_user -> GET /user/<user_id>
    simple retrieval of the public user information of the specified user,
    based on their ID
    '''
    info = db.User.get(user_id, False)
    return json.dumps(info)

from .database import errors, User, Session
from .decorators import datatype
import httplib
from tamari import password_hash, app
from flask import redirect, url_for, request, session, abort

__routes__ = {
    'login': '/login',
    'logout': '/logout',
    'user': '/user'
}
map(lambda name, route: app.endpoint(name, route),
    __routes__, __routes__.values())


@app.post(__routes__['user'])
@datatype
def register():
    ''' register -> POST /user/
        POST: username=[string]&password=[string]
    attempts to create/'register' a new user with the provided information,
    will return a CONFLICT error if the username already is registered.  If
    successful, the user id is stored in the session, logging in the user
    '''
    username = request.form['username']
    password = request.form['password']

    try:
        id, user = User.create({
            'username': username,
            'password': password_hash(password)
        })
    except errors.ExistingUsernameError:
        return httplib.CONFLICT

    session['id'] = str(id)
    session['rights'] = user['rights']

    return redirect(url_for('index')) if request.is_html else \
        (user, httplib.CREATED)


@app.post(__routes__['login'])
@datatype
def login():
    ''' login -> PUT /user/
    attempts a login with the provided information, if successful, stores the
    user's id in the session and returns the user information
    '''
    username = request.form['username']
    password = request.form['password']
    id, user = User.login(username, password_hash(password))
    if id:
        session['id'] = id
        session['rights'] = user['rights']
        return redirect(url_for('index')) if request.is_html else \
            (user, httplib.ACCEPTED)
    else:
        return "Invalid credentials", httplib.BAD_REQUEST


@app.get(__routes__['logout'])
@datatype
def logout():
    ''' logout -> GET /logout
    will delete the id reference for the user in the session, effectively
    logging the user out.
    '''
    Session.remove(session['_id'])
    session.clear()
    return redirect(url_for('index')) if request.is_html else httplib.ACCEPTED


@app.route(__routes__['user'] + '/<user_id>', methods=['DELETE'])
@datatype
def delete_user(user_id):
    ''' delete_user -> DELETE /user/<user_id>
    will try to delete the user's entry from the database and then log the user
    out
    '''
    if 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    elif session['id'] != user_id and 0 not in session['rights']:
        abort(httplib.UNAUTHORIZED)

    User.delete(user_id)
    return httplib.ACCEPTED


@app.get(__routes__['user'])
@datatype
def show_current():
    ''' show_current -> GET /user/
    simple retrieval of the user information at any time, same information
    that gets returned on a login
    '''
    if 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    info = User.get(session["id"], True)
    return info


@app.get(__routes__['user'] + '/<user_id>')
@datatype
def get_user(user_id):
    ''' get_user -> GET /user/<user_id>
    simple retrieval of the public user information of the specified user,
    based on their ID
    '''
    user = User.get(user_id, False)
    return user if user else httplib.BAD_REQUEST

from .database import errors, User
from .decorators import datatype
import httplib
from tamari import password_hash, app
from flask import request, session, abort

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
    ''' register -> POST /user
        POST: username=[string]&password=[string]

    Attempts to create/'register' a new user with the provided information,
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

    return user, httplib.CREATED


@app.post(__routes__['login'])
@datatype
def login():
    ''' login -> POST /login
        POST: username=[string]&password=[string]

    Attempts to authenticate with the provided credentials against any existing
    User entry on the system, if the credentials don't match any entry, a
    BAD_REQUEST is returned, else an ACCEPTED is returned along with the User
    information.  The session for the requester is then authenticated and
    acting as the user.
    '''
    username = request.form['username']
    password = request.form['password']
    id, user = User.login(username, password_hash(password))
    if id:
        session['id'] = id
        session['rights'] = user['rights']
        return user, httplib.ACCEPTED

    return "Invalid credentials", httplib.BAD_REQUEST


@app.get(__routes__['logout'])
@datatype
def logout():
    ''' logout -> GET /logout

    Voids the session using the clear method (defined in the session wrapper).
    This will empty the session information and remove the corresponding
    database entry, effectively removing the credentials and information that
    specifies the user in the application.
    '''
    session.clear()
    return httplib.ACCEPTED


@app.route(__routes__['user'] + '/<user_id>', methods=['DELETE'])
@datatype
def delete_user(user_id):
    ''' delete_user -> DELETE /user/<user_id>

    Deletes the user specified by the <user_id> route arg.  If the user_id does
    not correspond to an existing user on the application, a NOT_FOUND is
    returned.  If the user being deleted is not the current user and does not
    have administrative rights, an UNAUTHORIZED is returned.  If the deletion
    is successful, the user is logged out (if they are the same user as the
    one being deleted) and an ACCEPTED is returned.
    '''
    if 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    elif session['id'] != user_id and 0 not in session['rights']:
        abort(httplib.UNAUTHORIZED)

    try:
        User.delete(user_id)
        if session['id'] == user_id:
            session.clear()
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return httplib.ACCEPTED


@app.get(__routes__['user'])
@app.get(__routes__['user'] + '/<user_id>')
@datatype
def get_user(user_id=None):
    ''' get_user -> GET /user/<user_id>

    Retrieves the user that corresponds to the <user_id> route argument if it
    is specified.  If it is not, will retrieve the currently logged in user.
    If the user_id does not correspond to an existing user on the system a
    NOT_FOUND is returned.
    '''
    if not user_id and 'id' not in session:
        abort(httplib.UNAUTHORIZED)
    user_id = user_id if user_id else session['id']
    try:
        user = User.get(user_id, 'id' in session and user_id == session['id'])
    except errors.NoEntryError as err:
        return str(err), httplib.NOT_FOUND
    return user if user else httplib.NOT_FOUND

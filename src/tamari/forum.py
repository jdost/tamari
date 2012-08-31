import json
import httplib
from tamari import app
from db import db_errors

db = app.db
from flask import request, session, abort


JSON_KWARGS = {
    "separators": (',',':')
}

@app.route('/', methods=['GET'])
@app.route('/forum/<forum_id>', methods=['GET'])
def get_forums(forum_id=None):
    return json.dumps(db.Forum.get(level=forum_id), **JSON_KWARGS)

@app.route('/forum', methods=['POST'])
@app.route('/forum/<forum_id>', methods=['POST'])
def create_forum(forum_id=None):
    packet = {
        "name": request.form['name']
    }
    if forum_id:
        packet['parent'] = forum_id
    try:
        id = db.Forum.create(packet, session)
    except db_errors.BadPermissionsError:
        abort(httplib.UNAUTHORIZED)
    return str(id), httplib.CREATED

DEBUG = True
SECRET_KEY = "tamarisecretkeylulz"
SESSION_KEY = "tamari"
SESSION_DEFAULTS = {
    "date_format": "iso",
    "page_size": 25
}
DATABASE = {
    "type": "mongo",
    "info": {
        "host": "127.0.0.1",
        "port": 27017
    }
}
STATIC = {
    'folder': '../static',
    'path': '/s'
}
SERVING = {
    "host": "0.0.0.0",
    "port": 5055
}
INHERIT_ADMINS = True

from tamari.settings import settings
import db_errors

DEFAULT = "mongo"

if "db" in settings:
    db_type = settings["db"]["type"]
else:
    db_type = DEFAULT


def connect():
    if db_type == "mongo":
        import mongo
        return mongo
    else:
        raise db_errors.DBNotDefinedError('The database is not defined in ' +
                'the JSON settings file')

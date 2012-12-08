from sys import modules
from importlib import import_module
from .. import settings
import errors

DEFAULT = "mongo"
__submodules__ = ['User', 'Thread', 'Forum', 'Session']
__engines__ = ["mongo"]
__dict__ = modules[__name__].__dict__
engine = settings.DATABASE.get('type', DEFAULT)

if engine in __engines__:
    engine = import_module("." + engine, __name__)
    for submodule in __submodules__:
        __dict__[submodule] = import_module("." + submodule, engine.__name__)
    cleanup = engine.cleanup
else:
    raise errors.DBNotDefinedError(
        'The database is not defined in the settings file')

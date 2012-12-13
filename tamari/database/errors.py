'''
Collection of errors thrown by the DB layer modules based on various issues,
the names should be pretty self explanatory
'''


class DatabaseError(Exception):
    def __init__(self, *msg):
        self.message = msg[0].format(*msg[1:]) if len(msg) > 1 else msg[0]

    def __str__(self):
        return self.message


class MissingInfoError(DatabaseError):
    ''' MissingInfoError
    Raised by a db layer when information to be inserted into the DB is missing
    and is required.
    '''
    pass


class DBNotDefinedError(DatabaseError):
    ''' DBNotDefinedError
    Raised by the db initialization when there is information for the
    definition of the database that is missing
    '''
    pass


class ExistingUsernameError(DatabaseError):
    ''' ExistingUsernameError
    Raised by the db layer when trying to create a User with an username that
    already exists, which would cause an overlap
    '''
    pass


class BadPermissionsError(DatabaseError):
    ''' BadPermissionsError
    Raised by the db layer when a user lacks permission to perform a requested
    action
    '''
    pass


class NoEntryError(DatabaseError):
    ''' IncorrectIdError
    Raised by the db layer when a request using an ID returns nothing, mostly
    to signify that the ID provided is incorrect
    '''
    pass

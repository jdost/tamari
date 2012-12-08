'''
Collection of errors thrown by the DB layer modules based on various issues,
the names should be pretty self explanatory
'''


class MissingInfoError(Exception):
    ''' MissingInfoError
    Raised by a db layer when information to be inserted into the DB is missing
    and is required.
    '''
    pass


class DBNotDefinedError(Exception):
    ''' DBNotDefinedError
    Raised by the db initialization when there is information for the
    definition of the database that is missing
    '''
    pass


class ExistingUsernameError(Exception):
    ''' ExistingUsernameError
    Raised by the db layer when trying to create a User with an username that
    already exists, which would cause an overlap
    '''
    pass


class BadPermissionsError(Exception):
    ''' BadPermissionsError
    Raised by the db layer when a user lacks permission to perform a requested
    action
    '''
    pass


class IncorrectIdError(Exception):
    ''' IncorrectIdError
    Raised by the db layer when a request using an ID returns nothing, mostly
    to signify that the ID provided is incorrect
    '''
    pass

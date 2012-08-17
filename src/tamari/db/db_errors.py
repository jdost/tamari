class MissingInfoError(Exception):
    '''
MissingInfoError
    Raised by a db layer when information to be inserted into the DB is missing
    and is required.
    '''
    pass


class DBNotDefinedError(Exception):
    '''
DBNotDefinedError
    Raised by the db initialization when there is information for the
    definition of the database that is missing
    '''
    pass


class ExistingUsernameError(Exception):
    '''
ExistingUsernameError
    Raised by the db layer when trying to create a User with an username that
    already exists, which would cause an overlap
    '''
    pass

import unittest

VERBOSITY=1

if __name__ == '__main__':
    from tests.user import UserTest
    from tests.posts import PostTest
    from tests.api import APITest

    unittest.main(verbosity=VERBOSITY)

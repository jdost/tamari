import unittest

VERBOSITY=1

if __name__ == '__main__':
    from tests.user import UserTest
    from tests.threads import ThreadTest
    from tests.api import APITest
    from tests.forums import ForumTest

    unittest.main(verbosity=VERBOSITY)

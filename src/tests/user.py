from tests.base import TestBase
import json
import httplib


class UserTest(TestBase):
    ''' UserTest
    Test Suite to test the operations involving users, this includes creating,
    logging in, deleting, and getting public info vs private info (aka getting
    the information for another user or the one you are logged in as)
    '''
    user1 = {
        "username": "tester1",
        "password": "somehash"
    }
    user2 = {
        "username": "tester2",
        "password": "someotherhash"
    }

    def create_user(self, user):
        ''' UserTest::create_user
        Utility method to ease writing tests, action to create a test user with
        the provided information, checks success
        '''
        response = self.app.post('/user', data=user)
        self.assertHasStatus(response, httplib.CREATED)
        return response

    def logout_user(self):
        ''' UserTest::logout_user
        Utility method to ease writing tests, action to logout the current user
        and will test that the response succeeded
        '''
        response = self.app.get('/logout')
        self.assertHasStatus(response, httplib.ACCEPTED)

    def test_create_user(self):
        ''' UserTest::test_create_user
        Tests that a user is created and the basic operations on this state,
        including logging in as the user and looking up the user
        '''
        self.create_user(self.user1)

        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.OK)
        response_data = json.loads(response.data)
        self.assertEqual(self.user1["username"], response_data["username"])

    def test_good_login(self):
        ''' UserTest::test_good_login
        Tests that a user can be created, logout, and successfully log into
        the system with the same credentials
        '''
        self.create_user(self.user1)
        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.put('/user', data=self.user1)
        self.assertHasStatus(response, httplib.ACCEPTED)

    def test_bad_login(self):
        ''' UserTest::test_bad_login
        Tests that a user can be created, logout, and the login fails with the
        incorrect password (much like ::test_good_login except that the login
        should fail with the bad password)
        '''
        self.create_user(self.user1)
        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.put('/user', data={
            "username": self.user1['username'],
            "password": "~~"
        })
        self.assertHasStatus(response, httplib.BAD_REQUEST)

    def test_duplicate_user(self):
        ''' UserTest::test_duplicate_user
        Tests trying to create another user with the same username
        '''
        self.create_user(self.user1)
        self.logout_user()

        response = self.app.post('/user', data=self.user1)
        self.assertHasStatus(response, httplib.CONFLICT)

    def test_logout(self):
        ''' UserTest::test_logout
        Tests that the logout action successfully works
        '''
        self.create_user(self.user1)
        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.UNAUTHORIZED)

    def test_delete_user(self):
        ''' UserTest::test_delete_user
        Tests that the user can delete their account
        '''
        self.create_user(self.user1)
        response = self.app.get('/user')
        self.assertHasStatus(response, httplib.OK)

        response = self.app.delete('/user', data=self.user1)
        self.assertHasStatus(response, httplib.ACCEPTED)
        response = self.app.put('/user', data=self.user1)
        self.assertHasStatus(response, httplib.BAD_REQUEST)

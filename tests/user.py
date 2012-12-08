from base import TestBase
import json
import httplib


class UserTest(TestBase):
    ''' UserTest
    Test Suite to test the operations involving users, this includes creating,
    logging in, deleting, and getting public info vs private info (aka getting
    the information for another user or the one you are logged in as)
    '''
    user1 = {
        "username": "Tester1",
        "password": "Look I has a password"
    }
    user2 = {
        "username": "Tester2",
        "password": "Noez, they be stealin mah password"
    }

    def test_create_user(self):
        ''' Register a valid user
        Tests the creation of a new user works (register), then checks the
        data returned for the user as it is stored on the application.
        '''
        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CREATED)
        user = json.loads(response.data)
        self.assertIn("url", user)

        response = self.app.get(user["url"], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        response_data = json.loads(response.data)
        self.assertEqual(self.user1["username"], response_data["username"])

    def test_good_login(self):
        ''' Login with a valid user
        Tests the creation of a new user, logging out, and then successfully
        logging back into the system using the same credentials.
        '''
        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CREATED)

        self.assertTrue(self.logout())
        response = self.login(self.user1)
        self.assertHasStatus(response, httplib.ACCEPTED)

    def test_bad_login(self):
        ''' Login with a bad username//password pair
        Tests the creation of a new user, logging out, then then trying to
        login with a different password (like ::test_good_login except that
        the password is changed so that it should fail)
        '''
        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CREATED)

        self.logout()
        response = self.login({
            "username": self.user1['username'],
            "password": "~~"
        })
        self.assertHasStatus(response, httplib.BAD_REQUEST)

    def test_duplicate_user(self):
        ''' Register with an existing username
        Tests trying to register a user with a username that already exists
        '''
        self.assertHasStatus(self.register(self.user1), httplib.CREATED)
        self.assertTrue(self.logout())

        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CONFLICT)

    def test_logout(self):
        ''' Logout properly cleans the session
        Tests that the logout action successfully cleans the session
        information
        '''
        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CREATED)

        self.assertTrue(self.logout())

    def test_delete_user(self):
        ''' Delete a user account from the application
        Tests that a user account can be deleted from the application and that
        the account is properly removed from all storage.
        '''
        response = self.register(self.user1)
        self.assertHasStatus(response, httplib.CREATED)
        user = json.loads(response.data)

        response = self.app.delete(user['url'])
        self.assertHasStatus(response, httplib.ACCEPTED)
        response = self.app.get(user['url'])
        self.assertHasStatus(response, httplib.BAD_REQUEST)

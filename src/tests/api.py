from tests.base import TestBase
import httplib
import json


class APITest(TestBase):
    ''' APITest
    Test Suite to test the various operations that deal with API helper
    features.  Things dealing with session settings and permissions
    '''
    user = {
        "username": "apitester",
        "password": "justtest"
    }

    def create_user(self, user=None):
        ''' APITest::create_user
        Utility method to ease the creation of a new user on the server, will
        default to creating the class user if one is not defined
        '''
        if not user:
            user = self.user

        response = self.app.post('/user', data=user)
        self.assertHasStatus(response, httplib.CREATED)
        return response

    def get_settings(self):
        ''' APITest::get_settings
        Utility method to retrieve the currently visible settings from the
        current session
        '''
        response = self.app.get('/settings')
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def test_make_settings(self):
        ''' APITest::test_make_settings
        Tests that a setting can be made and that it gets saved, this is the
        basic operation test for using the session settings
        '''
        self.create_user()
        response = self.app.post('/settings', data={ "foo": "bar" })
        self.assertHasStatus(response, httplib.OK)

        settings = self.get_settings()
        self.assertEqual(settings["foo"], "bar")

    def test_prohibited_settings(self):
        ''' APITest::test_prohibited_settings
        Tests that you cannot modify/retrieve specific settings that should
        remain hidden from clients (internal session information)
        '''
        self.create_user()
        response = self.app.post('/settings', data={ "id": 1 })
        self.assertHasStatus(response, httplib.OK)  # should still succeed

        response = self.app.get('/user')  # if the id was changed, diff user
        self.assertHasStatus(response, httplib.OK)
        response_data = json.loads(response.data)
        self.assertEqual(self.user["username"], response_data["username"])

        response = self.app.post('/settings', data={ "_id": 1, "foo": "bar" })
        self.assertHasStatus(response, httplib.OK)
        settings = self.get_settings()
        self.assertEqual(settings["foo"], "bar")

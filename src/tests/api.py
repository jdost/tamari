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
    thread = {
        "title": "settings thread",
        "content": "settings thread stuff"
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

    def test_dateformat(self):
        ''' APITest::test_dateformat
        Tests that the date_format setting is properly working, this means
        testing 'epoch', 'iso', and the strftime strings
        '''
        import datetime, time
        def get_thread_dt(thread_id):  # short helper function
            response = self.app.get('/thread/' + thread_id)
            self.assertHasStatus(response, httplib.OK)
            return json.loads(response.data)["created"]
        # create the user & thread
        self.create_user()
        response = self.app.post('/thread', data=self.thread)
        self.assertHasStatus(response, httplib.CREATED)
        thread = response.data
        # test the ISO format, parses out a datetime object from this
        response = self.app.post('/settings', data={ "date_format": "iso" })
        self.assertHasStatus(response, httplib.OK)
        datetime_str = get_thread_dt(thread)
        datetime_obj = datetime.datetime.strptime(datetime_str,
                "%Y-%m-%dT%H:%M:%S.%f")
        # test the 'epoch' format, checks that it matchs the ISO dt object
        response = self.app.post('/settings', data={ "date_format": "epoch" })
        self.assertHasStatus(response, httplib.OK)
        datetime_int = get_thread_dt(thread)
        self.assertEqual(datetime_int, time.mktime(datetime_obj.timetuple()))
        # test a custom format, checks against the output of the ISO dt object
        response = self.app.post('/settings', data={ "date_format": "%d%%%m" })
        self.assertHasStatus(response, httplib.OK)
        datetime_str = get_thread_dt(thread)
        self.assertEqual(datetime_str, datetime_obj.strftime("%d%%%m"))

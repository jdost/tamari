from base import TestBase
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

    def get_settings(self):
        ''' APITest::get_settings
        Utility method to retrieve the currently visible settings from the
        current session
        '''
        response = self.app.get(
            self.endpoints['settings']['url'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def set_settings(self, settings):
        ''' APITest::set_settings
        Utility method to handle setting session settings for the current
        session with the provided dictionary.
        '''
        response = self.app.put(
            self.endpoints['settings']['url'], data=settings,
            headers=self.json_header)
        self.assertHasStatus(response, httplib.ACCEPTED)
        return response

    def test_make_settings(self):
        ''' Set session settings
        Tests that a setting can be made and that it gets saved, this is the
        basic operation test for using the session settings
        '''
        self.register(self.user)
        self.set_settings({"foo": "bar"})
        settings = self.get_settings()
        self.assertEqual(settings["foo"], "bar")

    def test_prohibited_settings(self):
        ''' Set session settings that are reserved
        Tests that you cannot modify/retrieve specific settings that should
        remain hidden from clients (internal session information)
        '''
        user = json.loads(self.register(self.user).data)
        self.set_settings({"id": 1})

        response = self.app.get(user["url"], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        response_data = json.loads(response.data)
        self.assertEqual(self.user["username"], response_data["username"])

        self.set_settings({"_id": 1, "foo": "bar"})
        settings = self.get_settings()
        self.assertEqual(settings["foo"], "bar")

    def test_dateformat(self):
        ''' Check dateformat settings
        Tests that the date_format setting is properly working, this means
        testing 'epoch', 'iso', and the strftime strings
        '''
        import datetime
        import time

        def get_thread_dt(thread_id):  # short helper function
            return self.get_thread(thread)["created"]
        # create the user & thread
        self.register(self.user)
        thread = self.create_thread(thread=self.thread)
        # test the ISO format, parses out a datetime object from this
        self.set_settings({"date_format": "iso"})
        datetime_str = get_thread_dt(thread)
        datetime_obj = datetime.datetime.strptime(
            datetime_str, "%Y-%m-%dT%H:%M:%S.%f")
        # test the 'epoch' format, checks that it matchs the ISO dt object
        self.set_settings({"date_format": "epoch"})
        datetime_int = get_thread_dt(thread)
        self.assertEqual(datetime_int, time.mktime(datetime_obj.timetuple()))
        # test a custom format, checks against the output of the ISO dt object
        self.set_settings({"date_format": "%d%%%m"})
        datetime_str = get_thread_dt(thread)
        self.assertEqual(datetime_str, datetime_obj.strftime("%d%%%m"))

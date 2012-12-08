import unittest
import tamari
import json
import httplib


class TestBase(unittest.TestCase):
    ''' TestBase
    This is the base class for all tests, takes care of the setup and teardown
    of the tests and includes some nice helper methods for more specialized
    asserts
    '''

    json_header = [('Accept', 'application/json')]
    default_user = {
        'username': 'Tester',
        'password': 'Look I has a password'
    }
    default_thread = {
        "title": "Testing thread",
        "content": "Testing tamari, hopefully this works as expected."
    }

    def register(self, user=None):
        ''' TestBase::register
        Helper method, performs the basic registration of a user using the
        provided credentials, returns the response.  If no credentials are
        provided, the TestBase::default_user set is used.
        '''
        user = user if user else self.default_user
        return self.app.post(
            self.endpoints["user"]["url"], data=user,
            headers=self.json_header)

    def login(self, credentials=None):
        ''' TestBase::login
        Helper method, performs the basic login of a user using the provided
        credentials, returns the response.  If no credentials are provided,
        the TestBase::default_user set is used.
        '''
        credentials = credentials if credentials else self.default_user
        return self.app.post(
            self.endpoints["login"]["url"], data=credentials,
            headers=self.json_header)

    def logout(self):
        ''' TestBase::logout
        Helper method, performs a logout on the current session, returns
        whether the logout action was successful.
        '''
        response = self.app.get(
            self.endpoints["logout"]["url"], headers=self.json_header)
        return response.status_code == httplib.ACCEPTED

    def get_forum(self, forum=None):
        ''' TestBase::get_forum
        Utility method to get the base forum data, checks for success and
        does the JSON parsing of the response data, returning the information
        on the requested forum.  If no forum is requested, will get the
        information for the root forum.
        '''
        forum = forum if forum else self.endpoints['root']
        response = self.app.get(forum['url'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def get_threads(self, forum=None):
        ''' TestBase::get_threads
        Utility method to get the list of threads for a forum.  Checks for
        succes, does the JSON parsing of the response data, returns the list
        of threads.  If no forum is requested, will get the thread list for
        the root forum.  If the forum requested is just a summary of a forum,
        will get the full information for the forum.
        '''
        if not forum:
            forum = self.endpoints['root']
        forum = forum if 'threads' in forum else self.get_forum(forum)
        response = self.app.get(forum['threads'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def create_thread(self, forum=None, thread=None):
        ''' TestBase::create_thread
        Utility method to create a test thread using the provided information,
        checks that the request succeeded
        '''
        if not forum:
            forum = self.endpoints['root']
        forum = forum if 'threads' in forum else self.get_forum(forum)
        thread = thread if thread else self.thread
        response = self.app.post(
            forum['threads'], data=thread, headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)
        return json.loads(response.data)

    def get_thread(self, thread):
        ''' TestBase::get_thread
        Utility method to get a specific thread as determined by the single
        argument, which should be from the thread list, checks the success and
        returns the JSON parsed thread information
        '''
        response = self.app.get(thread['url'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def setUp(self):
        ''' TestBase::setUp
        set up method for the test suite, creates a test client for the Flask
        application and sets the application testing flag
        '''
        tamari.app.config['TESTING'] = True
        tamari.app.debug = False
        self.app = tamari.app.test_client()
        response = self.app.get('/', headers=self.json_header)
        self.endpoints = json.loads(response.data)

    def tearDown(self):
        ''' TestBase::tearDown
        tear down method for the test suite
        '''
        tamari.cleanup()

    def assertEmpty(self, data, msg=None):
        ''' TestBase::assertEmpty
        wrapper for tests to check if a data set returned is empty, really is
        just used for readability
        '''
        self.assertEqual(len(data), 0, msg)

    def assertHasStatus(self, response, status, msg=None):
        ''' TestBase::assertHasStatus
        wrapper for tests to check if a response returns the correct HTTP
        status code
        params:
            response: <Response Object> returned from a test_client request
            status: <Int> for the expected status code or a <List> of the
                accepted status codes
            msg: <String> message to give to the assert call (default message
                is generated)
        '''
        if isinstance(status, list):
            if not msg:
                msg = "Response returned {} (expeded one of: {})".format(
                    response.status_code, str(status))
            self.assertIn(response.status_code, status, msg)
        else:
            if not msg:
                msg = "Response returned {} (expected: {})".format(
                    response.status_code, status)
            self.assertEqual(response.status_code, status, msg)

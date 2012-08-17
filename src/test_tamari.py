import unittest
import json
import tamari
import httplib

VERBOSITY=1


class TestBase(unittest.TestCase):
    ''' TestBase
    This is the base class for all tests, takes care of the setup and teardown
    of the tests and includes some nice helper methods for more specialized
    asserts
    '''

    def setUp(self):
        ''' TestBase::setUp
        set up method for the test suite, creates a test client for the Flask
        application and sets the application testing flag
        '''
        tamari.app.config['TESTING'] = True
        self.app = tamari.app.test_client()

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
            status: <Int> for the expected status code or a <List> of the accepted
                status codes
            msg: <String> message to give to the assert call (default message is
                generated)
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
        response = self.app.put('/user/', data=user)
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

        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.OK)
        response_data = json.loads(response.data)
        self.assertEqual(self.user1["username"], response_data["username"])

    def test_good_login(self):
        ''' UserTest::test_good_login
        Tests that a user can be created, logout, and successfully log into
        the system with the same credentials
        '''
        self.create_user(self.user1)
        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.post('/user/', data=self.user1)
        self.assertHasStatus(response, httplib.ACCEPTED)

    def test_bad_login(self):
        ''' UserTest::test_bad_login
        Tests that a user can be created, logout, and the login fails with the
        incorrect password (much like ::test_good_login except that the login
        should fail with the bad password)
        '''
        self.create_user(self.user1)
        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.post('/user/', data={
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

        response = self.app.put('/user/', data=self.user1)
        self.assertHasStatus(response, httplib.CONFLICT)

    def test_logout(self):
        ''' UserTest::test_logout
        Tests that the logout action successfully works
        '''
        self.create_user(self.user1)
        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.OK)

        self.logout_user()
        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.UNAUTHORIZED)

    def test_delete_user(self):
        ''' UserTest::test_delete_user
        Tests that the user can delete their account
        '''
        self.create_user(self.user1)
        response = self.app.get('/user/')
        self.assertHasStatus(response, httplib.OK)

        response = self.app.delete('/user/', data=self.user1)
        self.assertHasStatus(response, httplib.ACCEPTED)
        response = self.app.post('/user/', data=self.user1)
        self.assertHasStatus(response, httplib.BAD_REQUEST)


class PostTest(TestBase):
    ''' PostTest
    Test Suite to test the operations involving posts and threads
    '''
    user = {
        "username": "posttester",
        "password": "posts"
    }
    thread1 = {
        "title": "First test thread",
        "content": "This is just the first test thread, plenty to be done."
    }
    post1 = {
        "content": "This is just the first test reply post, plenty more."
    }

    def setUp(self):
        ''' PostTest::setUp
        Addition to the TestBase.setUp, creates a user to use in the thread
        actions
        '''
        TestBase.setUp(self)
        response = self.app.put('/user/', data=self.user)

    def get_threads(self):
        ''' PostTest::get_threads
        Utility method to get the list of threads, checks for success and
        does the JSON parsing of the response data, returning the array of
        threads
        '''
        response = self.app.get('/thread/')
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)["threads"]

    def get_thread(self, thread_id):
        ''' PostTest::get_thread
        Utility method to get a specific thread as determined by the single
        argument, which should be from the thread list, checks the success and
        returns the JSON parsed thread information
        '''
        response = self.app.get('/thread/' + thread_id)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def create_thread(self, thread):
        ''' PostTest::create_thread
        Utility method to create a test thread using the provided information,
        checks that the request succeeded
        '''
        response = self.app.put('/thread/', data=thread)
        self.assertHasStatus(response, httplib.CREATED)
        return response

    def test_get_empty_threads(self):
        ''' PostTest::test_get_empty_threads
        Simple test to see that the thread set is empty by default, if this is
        failing, most of the other tests will probably fail and something is
        wrong in the test setup
        '''
        threads = self.get_threads()
        self.assertEmpty(threads)

    def test_create_thread(self):
        ''' PostTest::test_create_thread
        Simple test to see that a thread can be created and retrieved, checks
        that the thread contains the proper data
        '''
        self.create_thread(self.thread1)
        threads = self.get_threads()
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                + "1 thread in it.")

        thread_id = threads[0]["id"]
        thread = self.get_thread(thread_id)
        self.assertEqual(thread['title'], self.thread1['title'], "Incorrect "
                + "title for the thread.")
        self.assertEqual(len(thread['posts']), 1, "Thread does not have the "
                + "correct number of posts, should be 1.")
        self.assertEqual(thread['posts'][0]['content'],
                self.thread1['content'], "Incorrect content on the post.")

    def test_replyto_thread(self):
        ''' PostTest::test_replyto_thread
        Tests that another user can reply to a thread
        '''
        self.create_thread(self.thread1)
        self.app.get('/logout')

        self.app.put('/user/', data={
            "username": "replytester",
            "password": "justreply"
        })
        threads = self.get_threads()
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                + "1 thread in it.")

        thread_id = threads[0]["id"]
        response = self.app.put("/thread/" + thread_id, data=self.post1)
        self.assertHasStatus(response, httplib.CREATED)
        thread = self.get_thread(thread_id)
        self.assertEqual(len(thread["posts"]), 2)


if __name__ == '__main__':
    unittest.main(verbosity=VERBOSITY)

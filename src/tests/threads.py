from tests.base import TestBase
import json
import httplib


class ThreadTest(TestBase):
    ''' ThreadTest
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
        ''' ThreadTest::setUp
        Addition to the TestBase.setUp, creates a user to use in the thread
        actions
        '''
        TestBase.setUp(self)
        response = self.app.post('/user', data=self.user)

    def get_threads(self):
        ''' ThreadTest::get_threads
        Utility method to get the list of threads, checks for success and
        does the JSON parsing of the response data, returning the array of
        threads
        '''
        response = self.app.get('/thread')
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def get_thread(self, thread_id):
        ''' ThreadTest::get_thread
        Utility method to get a specific thread as determined by the single
        argument, which should be from the thread list, checks the success and
        returns the JSON parsed thread information
        '''
        response = self.app.get('/thread/' + thread_id)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def create_thread(self, thread):
        ''' ThreadTest::create_thread
        Utility method to create a test thread using the provided information,
        checks that the request succeeded
        '''
        response = self.app.post('/thread', data=thread)
        self.assertHasStatus(response, httplib.CREATED)
        return response

    def test_get_empty_threads(self):
        ''' ThreadTest::test_get_empty_threads
        Simple test to see that the thread set is empty by default, if this is
        failing, most of the other tests will probably fail and something is
        wrong in the test setup
        '''
        threads = self.get_threads()
        self.assertEmpty(threads)

    def test_create_thread(self):
        ''' ThreadTest::test_create_thread
        Simple test to see that a thread can be created and retrieved, checks
        that the thread contains the proper data
        '''
        response = self.create_thread(self.thread1)
        thread_id_ = response.data
        threads = self.get_threads()
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                + "1 thread in it.")

        thread_id = threads[0]["id"]
        self.assertEqual(thread_id, thread_id_, "Thread ID returned from the "
                + "POST doesn't match the listing")
        thread = self.get_thread(thread_id)
        self.assertEqual(thread['title'], self.thread1['title'], "Incorrect "
                + "title for the thread.")
        self.assertEqual(len(thread['posts']), 1, "Thread does not have the "
                + "correct number of posts, should be 1.")
        self.assertEqual(thread['posts'][0]['content'],
                self.thread1['content'], "Incorrect content on the post.")

    def test_replyto_thread(self):
        ''' ThreadTest::test_replyto_thread
        Tests that another user can reply to a thread
        '''
        self.create_thread(self.thread1)
        self.app.get('/logout')

        self.app.post('/user', data={
            "username": "replytester",
            "password": "justreply"
        })
        threads = self.get_threads()
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                + "1 thread in it.")

        thread_id = threads[0]["id"]
        response = self.app.post("/thread/" + thread_id, data=self.post1)
        self.assertHasStatus(response, httplib.CREATED)
        thread = self.get_thread(thread_id)
        self.assertEqual(len(thread["posts"]), 2)

    def test_good_edit_thread(self):
        ''' ThreadTest::test_good_edit_thread
        Tests that editting a thread works correctly
        '''
        new_thread = {
            "title": "Editted thread title"
        }
        self.create_thread(self.thread1)
        threads = self.get_threads()
        response = self.app.put('/thread/' + threads[0]["id"],
                data=new_thread)
        self.assertHasStatus(response, httplib.ACCEPTED)

        threads = self.get_threads()
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["title"], new_thread["title"])

    def test_bad_edit_thread(self):
        ''' ThreadTest::test_bad_edit_thread
        Tests that editting a thread with the wrong user fails
        '''
        new_thread = {
            "title": "Editted thread title"
        }
        self.create_thread(self.thread1)
        self.app.get('/logout')

        self.app.post('/user', data={
            "username": "replytester",
            "password": "justreply"
        })
        threads = self.get_threads()
        response = self.app.put('/thread/' + threads[0]["id"],
                data=new_thread)
        self.assertHasStatus(response, httplib.UNAUTHORIZED)

    def test_good_edit_post(self):
        ''' ThreadTest::test_good_edit_post
        Tests that editting a post works correctly
        '''
        new_post = {
            "content": "This is the editted post content"
        }
        self.create_thread(self.thread1)
        threads = self.get_threads()
        thread_id = threads[0]["id"]
        thread = self.get_thread(thread_id)
        post_id = thread["posts"][0]["id"]

        response = self.app.put('/post/' + post_id, data=new_post)
        self.assertHasStatus(response, httplib.ACCEPTED)
        response = self.app.get('/post/' + post_id)
        post = json.loads(response.data)
        self.assertEqual(post['content'], new_post['content'])

    def test_bad_edit_post(self):
        ''' ThreadTest::test_bad_edit_post
        Tests that editting a post with the wrong user fails
        '''
        pass

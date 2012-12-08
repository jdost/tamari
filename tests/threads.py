from base import TestBase
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
        self.register(self.user)

    def test_get_empty_threads(self):
        ''' ThreadTest::test_get_empty_threads
        Simple test to see that the thread set is empty by default, if this is
        failing, most of the other tests will probably fail and something is
        wrong in the test setup
        '''
        root = self.get_forum()
        self.assertIn('threads', root)
        threads = self.get_threads(root)
        self.assertEmpty(threads)

    def test_create_thread(self):
        ''' ThreadTest::test_create_thread
        Simple test to see that a thread can be created and retrieved, checks
        that the thread contains the proper data
        '''
        root = self.get_forum()
        thread = self.create_thread(root, self.thread1)
        threads = self.get_threads(root)
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                         + "1 thread in it.")

        thread['url'] = threads[0]["url"]
        self.assertEqual(
            thread['url'], threads[0]['url'], "Thread ID "
            + "returned from the POST doesn't match the listing")
        thread = self.get_thread(thread)
        self.assertEqual(thread['title'], self.thread1['title'], "Incorrect "
                         + "title for the thread.")
        self.assertEqual(len(thread['posts']), 1, "Thread does not have the "
                         + "correct number of posts, should be 1.")
        self.assertEqual(
            thread['posts'][0]['content'],
            self.thread1['content'], "Incorrect content on the post.")

    def test_replyto_thread(self):
        ''' ThreadTest::test_replyto_thread
        Tests that another user can reply to a thread
        '''
        root = self.get_forum()
        self.create_thread(root, self.thread1)
        self.logout()

        self.register({
            "username": "replytester",
            "password": "justreply"
        })
        threads = self.get_threads(root)
        self.assertEqual(len(threads), 1, "Thread pool is empty, should have "
                         + "1 thread in it.")

        response = self.app.post(
            threads[0]["url"], data=self.post1, headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)
        thread = self.get_thread(threads[0])
        self.assertEqual(len(thread["posts"]), 2)

    def test_good_edit_thread(self):
        ''' ThreadTest::test_good_edit_thread
        Tests that editting a thread works correctly
        '''
        new_thread = {
            "title": "Editted thread title"
        }
        root = self.get_forum()

        self.create_thread(root, self.thread1)
        threads = self.get_threads(root)
        response = self.app.put(
            threads[0]["url"], data=new_thread, headers=self.json_header)
        self.assertHasStatus(response, httplib.ACCEPTED)

        threads = self.get_threads(root)
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["title"], new_thread["title"])

    def test_bad_edit_thread(self):
        ''' ThreadTest::test_bad_edit_thread
        Tests that editting a thread with the wrong user fails
        '''
        new_thread = {
            "title": "Editted thread title"
        }
        root = self.get_forum()

        self.create_thread(root, self.thread1)
        self.logout()

        self.register({
            "username": "replytester",
            "password": "justreply"
        })
        threads = self.get_threads(root)
        response = self.app.put(
            threads[0]["url"], data=new_thread, headers=self.json_header)
        self.assertHasStatus(response, httplib.UNAUTHORIZED)

    def test_good_edit_post(self):
        ''' ThreadTest::test_good_edit_post
        Tests that editting a post works correctly
        '''
        new_post = {
            "content": "This is the editted post content"
        }
        root = self.get_forum()

        self.create_thread(root, self.thread1)
        threads = self.get_threads(root)
        thread = self.get_thread(threads[0])
        post = thread["posts"][0]

        response = self.app.put(
            post["url"], data=new_post, headers=self.json_header)
        self.assertHasStatus(response, httplib.ACCEPTED)
        response = self.app.get(post["url"], headers=self.json_header)
        post = json.loads(response.data)
        self.assertEqual(post['content'], new_post['content'])

    def test_bad_edit_post(self):
        ''' ThreadTest::test_bad_edit_post
        Tests that editting a post with the wrong user fails
        '''
        pass

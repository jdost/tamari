from tests.base import TestBase
import json
import httplib


class ForumTest(TestBase):
    ''' ForumTest
    '''
    user = {
        "username": "forumtester",
        "password": "heyletstest"
    }

    def setUp(self):
        ''' ForumTest::setUp
        Additions to the TestBase.setUp, creates a user to use in the forum
        actions
        '''
        TestBase.setUp(self)
        response = self.app.post('/user', data=self.user)

    def get_forums(self, forum_id=None):
        ''' ForumTest::get_forums
        Utility function to ease getting the list of forums
        '''
        if forum_id:
            url = '/forum/' + forum_id
        else:
            url = '/'
        response = self.app.get(url)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def elevate_user(self):
        with self.app as app:
            with app.session_transaction() as session:
                session['permissions'] = [0]

    def test_empty_list(self):
        ''' ForumTest::test_empty_list
        Simple test to see if the initial forum list request for the root
        returns an empty list.
        '''
        forums = self.get_forums()
        self.assertEmpty(forums)

    def test_good_create_forum(self):
        ''' ForumTest::test_good_create_forum
        Creates a forum, makes sure it gets created and shows up in the list
        '''
        forum_data = {
            "name": "test forum"
        }
        self.elevate_user()
        response = self.app.post('/forum', data=forum_data)
        self.assertHasStatus(response, httplib.CREATED)
        forums = self.get_forums()
        self.assertEqual(1, len(forums))
        self.assertEqual(forums[0]["name"], forum_data["name"])

    def test_bad_create_forum(self):
        ''' ForumTest::test_bad_create_forum
        Tries to create a forum without the permissions, should fail
        '''
        forum_data = {
            "name": "bad forum"
        }
        response = self.app.post('/forum', data=forum_data)
        self.assertHasStatus(response, httplib.UNAUTHORIZED)
        forums = self.get_forums()
        self.assertEmpty(forums)

    def test_create_forum_thread(self):
        ''' ForumTest::test_create_forum_thread
        Creates a forum and then makes a thread in that forum
        '''
        forum_data = {
            "name": "test forum"
        }
        thread_data = {
            "title": "test thread",
            "content": "stuff should get posted"
        }
        self.elevate_user()
        response = self.app.post('/forum', data=forum_data)
        self.assertHasStatus(response, httplib.CREATED)
        forum_id = response.data

        forums = self.get_forums()
        self.assertEqual(1, len(forums))
        self.assertEqual(forums[0]["id"], forum_id)

        forums = self.get_forums(forum_id)
        self.assertEmpty(forums)
        response = self.app.get('/forum/' + forum_id + '/thread')
        self.assertHasStatus(response, httplib.OK)
        threads = json.loads(response.data)
        self.assertEmpty(threads)

        response = self.app.post('/forum/' + forum_id + '/thread',
                data=thread_data)
        self.assertHasStatus(response, httplib.CREATED)
        response = self.app.get('/forum/' + forum_id + '/thread')
        self.assertHasStatus(response, httplib.OK)
        threads = json.loads(response.data)

        self.assertEqual(1, len(threads))
        self.assertEqual(threads[0]["title"], thread_data["title"])

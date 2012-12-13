from base import TestBase
import json
import httplib


class ForumTest(TestBase):
    ''' ForumTest
    '''
    root_user = {
        "username": "ForumRoot",
        "password": "What is the meaning of life"
    }
    user = {
        "username": "Tester",
        "password": "I like to eat grass"
    }
    forum = {
        "name": "Test Subforum"
    }

    def setUp(self):
        ''' ForumTest::setUp
        Additions to the TestBase.setUp, creates a user to use in the forum
        actions
        '''
        TestBase.setUp(self)
        self.register(self.root_user)
        self.logout()
        self.register(self.user)

    def get_forums(self, forum=None):
        ''' ForumTest::get_forums
        Helper method that retrieves the list of subforums for a provided
        forum.  If no forum is specified, will use the root forum.
        '''
        forum = forum if forum else self.get_forum()
        response = self.app.get(forum['forums'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def create_forum(self, parent=None, forum=None):
        ''' ForumTest::create_forum
        Helper method that creates a subforum with the provided information.
        The forum created will be a child of `parent` and will be created with
        the information providided in `forum`.  If parent is not set, will use
        the root forum, if forum is not set, will use self.forum.
        '''
        parent = parent if parent else self.get_forum()
        forum = forum if forum else self.forum
        response = self.app.post(
            parent['forums'], data=forum, headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)
        return json.loads(response.data)

    def elevate_user(self):
        ''' ForumTest::elevate_user
        Helper method that elevates the current session's permissions up to
        root level.
        '''
        with self.app.session_transaction() as session:
                session['rights'].append(0)

    def test_empty_list(self):
        ''' Root forum has no subforums initially
        Simple test to see if the initial forum list request for the root
        returns an empty list.
        '''
        forums = self.get_forums()
        self.assertEmpty(forums)

    def test_good_create_forum(self):
        ''' Creates a subforum
        Creates a forum, makes sure it gets created and shows up in the list
        '''
        forum_data = {
            "name": "test forum"
        }
        self.elevate_user()

        root = self.get_forum()
        self.create_forum(root, forum_data)
        forums = self.get_forums(root)
        self.assertEqual(1, len(forums))
        self.assertEqual(forums[0]["name"], forum_data["name"])

    def test_bad_create_forum(self):
        ''' Create a forum without being logged in
        Tries to create a forum without the permissions, should fail
        '''
        forum_data = {
            "name": "bad forum"
        }

        root = self.get_forum()
        response = self.app.post(
            root['forums'], data=forum_data, headers=self.json_header)
        self.assertHasStatus(response, httplib.UNAUTHORIZED)
        forums = self.get_forums(root)
        self.assertEmpty(forums)

    def test_create_forum_thread(self):
        ''' Creates a thread in a new subforum
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

        root = self.get_forum()
        forum = self.create_forum(root, forum_data)

        forums = self.get_forums(root)
        self.assertEqual(1, len(forums))
        self.assertEqual(forums[0]["url"], forum["url"])

        forums = self.get_forums(forum)
        self.assertEmpty(forums)
        threads = self.get_threads(forum)
        self.assertEmpty(threads)

        self.create_thread(forum=forum, thread=thread_data)
        threads = self.get_threads(forum)

        self.assertEqual(1, len(threads))
        self.assertEqual(threads[0]["title"], thread_data["title"])

from base import TestBase
import json
import re
import httplib


class PageTest(TestBase):
    ''' PageTest
    Test Suite to test the paginating functionality.  The pagination is used
    to decrease load (for large forums and threads) by allowing either per
    request page sizing or via the settings structure.
    '''

    link_regex = "<(?P<url>[a-zA-Z0-9_\-;&=/?]+)>; rel=\"(?P<type>\w+)\""

    def create_n_threads(self, n=20):
        ''' PageTest::create_n_threads
        Helper method, just creates a set of test threads based on n (default
        is 20) to help test paging.
        '''
        for i in range(0, n):
            self.create_thread(thread={
                'title': 'Test thread ' + str(i),
                'content': 'page test'
            })

    def create_n_posts(self, thread=None, n=20):
        ''' PageTest::create_n_posts
        Helper method, just creates a series of test replies to a thread, that
        is either created already and passed in or a new thread will be created
        and returned.  Then loops through and creates the replies based on n
        (default is 20) to help test paging posts.
        '''
        if not thread:
            thread = self.create_thread(thread={
                'title': 'Paging test',
                'content': 'Post paging test'
            })

        for i in range(0, n):
            self.reply_to(thread, response={'content': 'Reply #' + str(i)})

        return thread

    def reply_to(self, thread, response):
        ''' PageTest::reply_to
        Helper method to handle the reply posting for a thread, this may get
        moved to the base set.
        '''
        response = self.app.post(
            thread["url"], data=response, headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)

    def get_links(self, response):
        ''' PageTest::get_links
        Helper method, parses out the URLs and their targets and returns as a
        dictionary, will probably reuse this code in the various libs for
        handling the paging.
        '''
        self.assertIn('Link', response.headers)
        links = re.findall(self.link_regex, response.headers.get('Link'))
        return dict(map(lambda h: (h[1], h[0]), links))

    def setUp(self):
        TestBase.setUp(self)
        self.register()

    def test_forum_url(self):
        ''' Check the forum pages correctly via URL params
        Uses URL query params to set the page size and page number for the
        request.  This will create a number of threads and then request the
        root forum thread list, this list should be limited based on the URL
        param
        '''
        page_size = 5

        root = self.get_forum()
        self.create_n_threads()

        response = self.app.get(
            root['threads'], headers=self.json_header,
            query_string={"per_page": page_size})
        self.assertHasStatus(response, httplib.OK)
        threads = json.loads(response.data)
        self.assertIn("Link", response.headers)
        self.assertEqual(page_size, len(threads))

    def test_forum_settings(self):
        ''' Check the forum pages correctly via session settings
        Uses the session settings infrastructure to set the page size to a
        default (and avoid adding it to all requests).  Then creates a number
        of threads and requests the thread list, this list should be limited
        based on the value set in the session.
        '''
        page_size = 5

        root = self.get_forum()
        self.create_n_threads()

        response = self.app.put(
            self.endpoints['settings']['url'], data={"page_size": page_size},
            headers=self.json_header)
        self.assertHasStatus(response, httplib.ACCEPTED)

        response = self.app.get(
            root['threads'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        threads = json.loads(response.data)
        self.assertIn("Link", response.headers)
        self.assertEqual(page_size, len(threads))

    def test_thread_url(self):
        ''' Check the thread pages correctly via URL params
        Uses URL query params to set the page size and page number for the
        request.  This will create a number of replies and then request the
        thread's post list, this list should be limited based on the URL param
        '''
        page_size = 5

        root = self.get_forum()
        thread = self.create_thread(forum=root)
        self.create_n_posts(thread)

        response = self.app.get(
            thread['url'], headers=self.json_header,
            query_string={"per_page": page_size})
        self.assertHasStatus(response, httplib.OK)
        full_thread = json.loads(response.data)
        self.assertIn("Link", response.headers)
        self.assertEqual(page_size, len(full_thread['posts']))

    def test_thread_settings(self):
        ''' Check the thread pages correctly via session settings
        Uses the session settings infrastructure to set the page size to a
        default (and avoid adding it to all requests).  Then creates a number
        of replies and requests the thread, this list should be limited
        based on the value set in the session.
        '''
        page_size = 5

        root = self.get_forum()
        thread = self.create_thread(forum=root)
        self.create_n_posts(thread)

        response = self.app.put(
            self.endpoints['settings']['url'], data={"page_size": page_size},
            headers=self.json_header)
        self.assertHasStatus(response, httplib.ACCEPTED)

        response = self.app.get(
            thread['url'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        full_thread = json.loads(response.data)
        self.assertIn("Link", response.headers)
        self.assertEqual(page_size, len(full_thread['posts']))

    def test_next_page(self):
        ''' Check that the Link URLs work for a paged request
        Uses a URL query param to set the page size for the request of a paged
        forum thread list, then uses the URLs in the Link header to get the
        next page for the list, making sure this works.
        '''
        page_size = 5

        root = self.get_forum()
        self.create_n_threads()

        response = self.app.get(
            root['threads'], headers=self.json_header,
            query_string={"per_page": page_size})
        self.assertHasStatus(response, httplib.OK)
        threads = json.loads(response.data)
        self.assertEqual(page_size, len(threads))

        links = self.get_links(response)
        self.assertIn('next', links)

        response = self.app.get(links['next'], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        threads_ = json.loads(response.data)
        self.assertEqual(page_size, len(threads_))
        self.assertNotEqual(threads, threads_)

        links = self.get_links(response)
        self.assertIn('prev', links)
        self.assertIn('next', links)

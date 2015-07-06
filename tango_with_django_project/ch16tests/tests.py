import sys

from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys

import populate_rango
import test_utils
from rango.models import Page


class Chapter16ViewTests(TestCase):
    def test_count_category_views(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        #Access a category 10 times
        for i in xrange(1, 11):
            response = self.client.get('/rango/category/' + categories[0].slug + '/')

            # Check it has the correct number of views
            self.assertContains(response, 'Category views: ' + str(i))

    def test_count_page_views(self):
        #Create categories and 2 pages for category 1 with 0 views
        categories = test_utils.create_categories()
        page1 = Page(category=categories[0], title="Page 1", url="http://www.page1.com")
        page1.save()
        page2 = Page(category=categories[0], title="Page 2", url="http://www.page2.com")
        page2.save()

        # Access page 1 one time
        self.client.get('/rango/goto/?page_id=' + str(page1.id))

        #Access page 2 ten times
        for i in xrange(1, 11):
            self.client.get('/rango/goto/?page_id=' + str(page2.id))

        #Access Category 1
        response = self.client.get('/rango/category/' + categories[0].slug + '/')

        # Check the pages have the correct number of views
        self.assertContains(response, '<li><a href="/rango/goto/?page_id=' + str(page1.id) + '">Page 1</a> (1 view)</li>', html=True)
        self.assertContains(response, '<li><a href="/rango/goto/?page_id=' + str(page2.id) + '">Page 2</a> (10 views)</li>', html=True)

    def test_pages_are_displayed_in_most_viewed_order(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        # For each category check that the first page in its context
        # has more views than the second one.
        for category in categories:
            context = self.client.get('/rango/category/' + category.slug + '/').context
            self.assertGreater(context['pages'][0].views, context['pages'][1].views)

    def test_page_redirection(self):
        #Populate database with real pages
        populate_rango.populate()
        pages = Page.objects.all()

        for page in pages:
            response = self.client.get('/rango/goto/?page_id=' + str(page.id))
            self.assertRedirects(response, page.url, fetch_redirect_response=False)


class Chapter16LiveServerTestCase(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_category_likes_and_views(self):
        #Populate database
        populate_rango.populate()

        #Access index
        self.browser.get(self.live_server_url + '/rango/')

        # Click Python category
        self.browser.find_element_by_link_text("Python").click()

        # Check the current number of likes and views
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('64 people like this category', body_text)
        self.assertIn('Category views: 129', body_text)

        # Check button like does not exist because user is not logged in
        self.assertRaises(NoSuchElementException, self.browser.find_element_by_id, 'likes')

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)

        # Navigate back to Python category
        self.browser.find_element_by_link_text("Python").click()

        # Click like button and check the number of likes increased by one
        self.browser.find_element_by_id('likes').click()

        #Wait for AJAX response
        wait = WebDriverWait(self.browser, 3)
        like_button = wait.until(EC.invisibility_of_element_located((By.ID, 'likes')))
        body_text = self.browser.find_element_by_tag_name('body').text

        #Check number of likes and views have increased by 1
        self.assertIn('65 people like this category', body_text)
        self.assertIn('Category views: 130', body_text)


        # Check button like is not present anymore
        self.assertFalse(like_button.is_displayed())

    def test_page_views(self):
        #TODO check it works on other systems
        #Check if on Mac keyboard
        control_key = Keys.CONTROL

        if sys.platform == 'darwin':
            control_key = Keys.COMMAND

        #Populate database
        populate_rango.populate()

        #Access index
        self.browser.get(self.live_server_url + '/rango/')

        # Click in Python category link
        self.browser.find_element_by_link_text('Python').click()

        #Access Python pages
        # 5 times
        for i in xrange(0, 5):
            self.browser.find_element_by_link_text('Official Python Tutorial').send_keys(control_key + Keys.RETURN);

        # 3 times
        for i in xrange(0, 3):
            self.browser.find_element_by_link_text('Learn Python in 10 Minutes').send_keys(control_key + Keys.RETURN);

        # 1 time
        self.browser.find_element_by_link_text('How to Think like a Computer Scientist').send_keys(control_key + Keys.RETURN);

        # Click in Python category link again
        self.browser.find_element_by_link_text('Python').click()

        # Check if they are correctly displayed
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Official Python Tutorial (5 views)', body_text)
        self.assertIn('Learn Python in 10 Minutes (3 views)', body_text)
        self.assertIn('How to Think like a Computer Scientist (1 view)', body_text)
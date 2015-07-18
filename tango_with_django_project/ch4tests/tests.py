from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.core.urlresolvers import reverse

# Create your tests here.
class Chapter4LiveServerTests(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_navigate_from_index_to_about(self):
        # Go to rango main page
        self.browser.get(self.live_server_url + reverse('index'))

        # Search for a link to About page
        about_link = self.browser.find_element_by_partial_link_text("About")
        about_link.click()

        # Check if it goes back to the home page
        self.assertEqual(self.live_server_url + reverse('about'), self.browser.current_url)

    def test_navigate_from_about_to_index(self):
        # Go to rango main page
        self.browser.get(self.live_server_url + reverse('about'))

        # Check if there is a link back to the home page
        link_to_home_page = self.browser.find_element_by_tag_name('a')
        link_to_home_page.click()

        # Check if it goes back to the home page
        self.assertEqual(self.live_server_url + reverse('index'), self.browser.current_url)

class Chapter4ViewTests(TestCase):
    def test_index_contains_hello_message(self):
        # Check if there is the message 'hello world!'
        response = self.client.get(reverse('index'))
        self.assertIn('Rango says', response.content)

    def test_about_contains_create_message(self):
        # Check if in the about page is there a message
        response = self.client.get(reverse('about'))
        self.assertIn('This tutorial has been put together by', response.content)


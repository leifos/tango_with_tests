import sys

from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
from django.conf import settings
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys

import populate_rango
import test_utils
from rango.models import Page
from django.core.urlresolvers import reverse, NoReverseMatch

class Chapter16ViewTests(TestCase):
    # Click through and like collection tests
    def test_count_category_views(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        #Access a category 10 times
        for i in xrange(1, 11):
            response = self.client.get(reverse('category', args=[categories[0].slug]))

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
        self.client.get(reverse('goto') + '?page_id=' + str(page1.id))

        #Access page 2 ten times
        for i in xrange(1, 11):
            self.client.get(reverse('goto') + '?page_id=' + str(page2.id))

        #Access Category 1
        response = self.client.get(reverse('category', args=[categories[0].slug]))

        # Check the pages have the correct number of views
        self.assertContains(response, '<li><a href="' + reverse('goto') + '?page_id='
                            + str(page1.id) +'">Page 1</a> (1 view)</li>', html=True)
        self.assertContains(response, '<li><a href="' + reverse('goto') + '?page_id='
                            + str(page2.id) + '">Page 2</a> (10 views)</li>', html=True)

    def test_pages_are_displayed_in_most_viewed_order(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        # For each category check that the first page in its context
        # has more views than the second one.
        for category in categories:
            context = self.client.get(reverse('category', args=[category.slug])).context
            self.assertGreater(context['pages'][0].views, context['pages'][1].views)

    def test_page_redirection(self):
        #Populate database with real pages
        populate_rango.populate()
        pages = Page.objects.all()

        for page in pages:
            response = self.client.get(reverse('goto') + '?page_id=' + str(page.id))
            self.assertRedirects(response, page.url, fetch_redirect_response=False)

    # Category filter and search within categories

    def test_only_logged_in_users_can_search(self):
        # Create categories and user
        categories = test_utils.create_categories()
        test_utils.create_user()

        # Access a category page
        response = self.client.get(reverse('category', args=[categories[0].slug]))

        # Check if it contains button Search - it should not
        self.assertNotContains(response, 'Search')

        # Log user in
        self.client.login(username='testuser', password='test1234')

        # Access a category page
        response = self.client.get(reverse('category', args=[categories[0].slug]))

        # Check if it contains button Search - it now should
        self.assertContains(response, 'Search')

    def test_search_page_no_longer_exists(self):
        # Try to access search page -> 404 or NoReverseMatch
        try:
            response = self.client.get(reverse('search'))
            self.assertEquals(response.status_code, 404)
        except:
            self.assertRaises(NoReverseMatch, reverse, 'search')


    def test_index_no_longer_contain_search_link(self):
        # Access index
        response = self.client.get(reverse('index'))

        # Check if it does not have a clicable link for search
        self.assertNotContains(response, 'Search', html=True)


    def test_link_to_edit_profile_in_index(self):
        #Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access index
        response = self.client.get(reverse('index'))

        # Check there is a link to edit profile
        self.assertContains(response, '<a href="' + reverse('edit_profile') + '">Edit Profile</a>', html=True)

    def test_registration_redirects_to_profile_form_after_registration(self):
        #  Register user
        response = self.client.post(reverse('registration_register'),
                         {'username': 'testuser', 'password1':'test1234',
                          'email':'testuser@testuser.com', 'password2':'test1234' }, follow=True)

        # Assert it was redirected to edit profile
        self.assertRedirects(response, reverse('edit_profile'))

class Chapter16LiveServerTestCase(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    # Click through and like collection tests

    def test_category_likes_and_views(self):
        #Populate database
        populate_rango.populate()

        #Access index
        self.browser.get(self.live_server_url + reverse('index'))

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
        self.browser.get(self.live_server_url + reverse('index'))

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

    def test_category_filter_on_sidebar(self):
        # Populate database
        populate_rango.populate()

        # Access index
        self.browser.get(self.live_server_url + reverse('index'))

        # Types an existing category - Python
        suggestion_field = self.browser.find_element_by_id('suggestion')
        suggestion_field.send_keys('P')
        sidebar_text = self.browser.find_element_by_id('cats').text

        # Check Python category is displayed, but Django isn't
        self.assertIn('Python', sidebar_text)
        self.assertNotIn('Django', sidebar_text)

        # Types an existing category - Django
        suggestion_field.clear()
        suggestion_field.send_keys('D')
        sidebar_text = self.browser.find_element_by_id('cats').text

        # Check Django category is displayed, but Python isn't
        self.assertNotIn('Python', sidebar_text)
        self.assertIn('Django', sidebar_text)

        # Types an not existing category
        suggestion_field.clear()
        suggestion_field.send_keys('Java')
        sidebar_text = self.browser.find_element_by_id('cats').text

        # Check neither Python or Django are displayed, but a message no categories
        self.assertNotIn('Python', sidebar_text)
        self.assertNotIn('Django', sidebar_text)
        self.assertIn('There are no category present.', sidebar_text)

    def test_category_filter_shows_up_to_eight_categories(self):
        # Create fake categories
        categories = test_utils.create_categories()

        # Access index
        self.browser.get(self.live_server_url + reverse('index'))

        # Check all categories are displayed
        body_text = self.browser.find_element_by_tag_name('body').text
        for category in categories:
            self.assertIn(category.name, body_text)

        # Types 'c' which is valid for all categories - Should display only 8
        suggestion_field = self.browser.find_element_by_id('suggestion')
        suggestion_field.send_keys('c')
        sidebar_text = self.browser.find_element_by_id('cats').text

        # Check categories 1 - 8 are displayed
        for category in categories[:8]:
            self.assertIn(category.name, sidebar_text)

        # Check categories 9 and 10 are not displayed
        for category in categories[8:]:
            self.assertNotIn(category.name, sidebar_text)

    def test_search_uses_ajax(self):
        # Populate database
        populate_rango.populate()

        # Access login page
        self.browser.get(self.live_server_url + reverse('auth_login'))
        test_utils.login(self)

        # Navigate to Python category
        self.browser.find_element_by_link_text("Python").click()

        # Check the number of views for Python category
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Category views: 129', body_text)

        # Click search button
        self.browser.find_element_by_name('submit').click()

        # Check an error occurs as results were not yet retrieved
        self.assertRaises(AssertionError, self.assertIn, 'Results', body_text)

        #Wait for AJAX response
        wait = WebDriverWait(self.browser, 3)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'list-group')))
        body_text = self.browser.find_element_by_tag_name('body').text

        # Check results label are now displayed
        self.assertIn('Results', body_text)

        # Check the number of views for Python category did not change
        self.assertIn('Category views: 129', body_text)

    def test_user_search_within_categories(self):
        # Populate database
        populate_rango.populate()

        # Access index
        self.browser.get(self.live_server_url + reverse('index'))

        # Navigate back to Python category
        self.browser.find_element_by_link_text("Python").click()

        # Check there is not a button for search
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Search', body_text)

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)

        # Navigate back to Python category
        self.browser.find_element_by_link_text("Python").click()

        # Check search box contains Python in it
        search_field = self.browser.find_element_by_name('query')
        self.assertEquals(search_field.get_attribute('value'), 'Python')

        # Click search button
        self.browser.find_element_by_name('submit').click()

        #Wait for AJAX response
        wait = WebDriverWait(self.browser, 3)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'list-group')))
        body_text = self.browser.find_element_by_tag_name('body').text

        # Check results label
        self.assertIn('Results', body_text)

        #Check 10 results are displayed
        results_list = self.browser.find_elements_by_class_name('list-group-item')
        self.assertEquals(len(results_list), 10)

        # Check results mention Python
        for result in results_list:
            self.assertIn('Python', result.text)

    def test_users_can_view_their_profiles(self):
        # Access index
        self.browser.get(self.live_server_url + reverse('index'))

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)

        # Access view profile and check information
        self.browser.find_element_by_link_text("View Profile").click()
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('admin Profile', body_text)
        self.assertIn('Email: admin@admin.com', body_text)

        # Assert image is the default one
        img_source = self.browser.find_element_by_tag_name('img').get_attribute("src")
        self.assertIn('default', img_source)

    def test_user_register_and_add_profile(self):
        #Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        #Click in Register
        self.browser.find_element_by_link_text('Register Here').click()

        # Fill registration form
        # username
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('testuser')

        # email
        email_field = self.browser.find_element_by_name('email')
        email_field.send_keys('testuser@testuser.com')

        # password1
        password_field = self.browser.find_element_by_name('password1')
        password_field.send_keys('test1234')

        # password2
        password2_field = self.browser.find_element_by_name('password2')
        password2_field.send_keys('test1234')

        # Submit
        password2_field.send_keys(Keys.RETURN)

        # It should be redirected to edit profile page
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Profile Details', body_text)
        self.assertIn('testuser profile', body_text)

        # Find website field and fills it
        self.browser.find_element_by_id("id_website").send_keys("http://www.testuser.com")

        # Check user has a default picture and upload a new picture
        self.browser.find_element_by_id("id_picture").send_keys(os.getcwd() + settings.MEDIA_URL + 'rango.jpg')

        # Submit form
        self.browser.find_element_by_name("submit").click()

        # Check it is in index page
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Rango says... hello testuser!', body_text)

        # Access view profile and check information
        self.browser.find_element_by_link_text("View Profile").click()
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('testuser Profile', body_text)
        self.assertIn('Email: testuser@testuser.com', body_text)

        # Assert image was uploaded and it is not the default one
        img_source = self.browser.find_element_by_tag_name('img').get_attribute("src")
        self.assertNotIn('default', img_source)
        self.assertIn('_testuser', img_source)


    def test_users_can_edit_their_profiles(self):
        #Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)

        # Access edit profile
        self.browser.find_element_by_link_text('Edit Profile').click()

        # Find website field, check it is empty and fills it
        website_field = self.browser.find_element_by_id("id_website")
        self.assertEquals(website_field.get_attribute("value"), "")
        website_field.send_keys("http://www.testuser.com")

        # Check user has a default picture and upload a new picture
        img_source = self.browser.find_element_by_tag_name('img').get_attribute("src")
        self.assertIn(settings.MEDIA_URL + 'profile_images/default', img_source)
        self.browser.find_element_by_id("id_picture").send_keys(os.getcwd() + settings.MEDIA_URL + 'rango.jpg')

        # Submit form
        self.browser.find_element_by_name("submit").click()

    def test_users_can_see_a_list_of_users(self):
        # Create users
        users_list = test_utils.create_users()

        #Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)


        #Click in Users Profile
        self.browser.find_element_by_link_text('View Users Profiles').click()
        body_text = self.browser.find_element_by_tag_name('body').text

        # Check the list contains all the users
        for user in users_list:
            self.assertIn(user[0].username, body_text)
            self.assertIn(user[0].email, body_text)

    def test_users_can_edit_only_their_own_page(self):
        # Create users
        users_list = test_utils.create_users()

        #Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # User click Login link and logs in
        self.browser.find_element_by_link_text('Login').click()
        test_utils.login(self)

        #Click in Users Profile
        self.browser.find_element_by_link_text('View Users Profiles').click()

        # For each user in the list access it and check if it is not possible to edit its profile
        # Check there is not a button to click 'edit profile'
        for user in users_list:
            self.browser.find_element_by_link_text(user[0].username).click()
            # Check it is on its profile
            body_text = self.browser.find_element_by_tag_name('body').text
            self.assertIn(user[0].username + ' Profile', body_text)

            self.assertRaises(NoSuchElementException, self.browser.find_element_by_id, 'id_edit_profile')
            self.browser.find_element_by_link_text('View Users Profiles').click()

        # Check that admin user can view the button as it is logged
        self.browser.find_element_by_link_text('admin').click()
        self.browser.find_element_by_id('id_edit_profile').click()

        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Profile Details', body_text)
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rango.models import User, UserProfile, Category
from rango.forms import UserForm, UserProfileForm
import test_utils
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.conf import settings
import os.path

class Chapter9LiveServerTests(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_register_user(self):
        #Access index page
        self.browser.get(self.live_server_url + '/rango/')

        #Click in Register
        self.browser.find_elements_by_link_text('Register Here')[0].click()

        # Fill registration form
        # username
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('testuser')

        # email
        email_field = self.browser.find_element_by_name('email')
        email_field.send_keys('testuser@testuser.com')

        # password
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('test1234')

        # website
        website_field = self.browser.find_element_by_name('website')
        website_field.send_keys('http://www.testuser.com')

        # Submit
        website_field.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')

        # Check for success message
        self.assertIn('Rango says: thank you for registering!', body.text)
        self.browser.find_element_by_link_text('Return to the homepage.')

    def test_admin_contains_user_profile(self):
        # Access admin page
        self.browser.get(self.live_server_url + '/admin/')

        # Log in the admin page
        test_utils.login(self)

        # Check exists a link to user profiles
        self.browser.find_element_by_link_text('User profiles').click()

        # Check it is empty
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('0 user profiles', body.text)

        # create a user
        user, user_profile = test_utils.create_user()

        self.browser.refresh()

        # Check there is one profile
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(user.username, body.text)

    def test_links_in_index_page_when_logged(self):
        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        #Check links that appear for logged person only
        self.browser.find_element_by_link_text('Add a New Category')
        self.browser.find_element_by_link_text('Restricted Page')
        self.browser.find_element_by_link_text('Logout')
        self.browser.find_element_by_link_text('About')

        # Check that links does not appears for logged users
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Login', body.text)
        self.assertNotIn('Register Here', body.text)

    def test_links_in_index_page_when_not_logged(self):
        #Access index page
        self.browser.get(self.live_server_url + '/rango/')

        #Check links that appear for not logged person only
        self.browser.find_element_by_link_text('Register Here')
        self.browser.find_element_by_link_text('Login')
        self.browser.find_element_by_link_text('About')

        # Check that links does not appears for not logged users
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Add a New Category', body.text)
        self.assertNotIn('Restricted Page', body.text)
        self.assertNotIn('Logout', body.text)

    def test_logout_link(self):
        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        #Clicks to logout
        self.browser.find_element_by_link_text('Logout').click()

        # Check if it see log in link, thus it is logged out
        self.browser.find_element_by_link_text('Login')


    def test_add_category_when_logged(self):
        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        # Click category
        self.browser.find_element_by_partial_link_text('Add a New Category').click()

        # Types new category name
        username_field = self.browser.find_element_by_name('name')
        username_field.send_keys('New Category')

        # Click on Create Category
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if New Category appears in the index page
        self.assertIn('New Category', body.text)

    def test_add_category_when_not_logged(self):
        #Access add category page
        self.browser.get(self.live_server_url + '/rango/add_category/')

        # Check login form is displayed
        # username
        self.browser.find_element_by_name('username')

        # password
        self.browser.find_element_by_name('password')


    def test_add_page_when_logged(self):
        #Create categories
        test_utils.create_categories()

        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        # Click category
        self.browser.find_element_by_partial_link_text('Category').click()

        # Click add page
        self.browser.find_element_by_partial_link_text("Add a Page").click()

        # Types new page name
        username_field = self.browser.find_element_by_name('title')
        username_field.send_keys('New Page')

        # Types url for the page
        username_field = self.browser.find_element_by_name('url')
        username_field.send_keys('http://www.newpage.com')

        # Click on Create Page
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if New Page appears in the category page
        self.assertIn('New Page', body.text)

    def test_add_page_when_not_logged(self):
        #Create categories
        test_utils.create_categories()

        # Access index
        self.browser.get(self.live_server_url + '/rango/')

        # Click category
        self.browser.find_element_by_partial_link_text('Category').click()

        # Check it does not have a link to add page
        body = self.browser.find_element_by_tag_name('body')
        self.assertNotIn('Add a Page', body.text)

        # Access add page directly
        category = Category.objects.all()[0]
        self.browser.get(self.live_server_url + '/rango/category/' + category.slug + '/add_page/')

        # Check login form is displayed
        # username
        self.browser.find_element_by_name('username')

        # password
        self.browser.find_element_by_name('password')

    def test_access_restricted_page_when_logged(self):
        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        # Access restricted page
        self.browser.find_element_by_link_text('Restricted Page').click()

        # Check that a message is displayed
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn("Since you're logged in, you can see this text!", body.text)

    def test_access_restricted_page_when_not_logged(self):
        # Access restricted page
        self.browser.get(self.live_server_url + '/rango/restricted/')

        # Check login form is displayed
        # username
        self.browser.find_element_by_name('username')

        # password
        self.browser.find_element_by_name('password')

    def test_logged_user_message_in_index(self):
        # Access login page
        self.browser.get(self.live_server_url + '/rango/login/')

        # Log in
        test_utils.login(self)

        # Check for the username in the message
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('hello admin', body.text)

class Chapter9ModelTests(TestCase):
    def test_user_profile_model(self):
        # Create a user
        user, user_profile = test_utils.create_user()

        # Check there is only the saved user and its profile in the database
        all_users = User.objects.all()
        self.assertEquals(len(all_users), 1)

        all_profiles = UserProfile.objects.all()
        self.assertEquals(len(all_profiles), 1)

        # Check profile fields were saved correctly
        all_profiles[0].user = user
        all_profiles[0].website = user_profile.website

class Chapter9ViewTests(TestCase):
    def test_registration_form_is_displayed_correctly(self):
        #Access registration page
        response = self.client.get('/rango/register/')

        # Check if form is rendered correctly
        self.assertIn('<h1>Register with Rango</h1>', response.content)
        self.assertIn('Rango says: <strong>register here!</strong><br />', response.content)

        # Check form in response context is instance of UserForm
        self.assertTrue(isinstance(response.context['user_form'], UserForm))

        # Check form in response context is instance of UserProfileForm
        self.assertTrue(isinstance(response.context['profile_form'], UserProfileForm))

        user_form = UserForm()
        profile_form = UserProfileForm()

        # Check form is displayed correctly
        self.assertEquals(response.context['user_form'].as_p(), user_form.as_p())
        self.assertEquals(response.context['profile_form'].as_p(), profile_form.as_p())

        # Check submit button
        self.assertIn('type="submit" name="submit" value="Register"', response.content)


    def test_login_form_is_displayed_correctly(self):
        #Access login page
        response = self.client.get('/rango/login/')

        #Check form display
        #Header
        self.assertIn('<h1>Login to Rango</h1>', response.content)

        #Username label and input text
        self.assertIn('Username:', response.content)
        self.assertIn('input type="text" name="username" value="" size="50"', response.content)

        #Password label and input text
        self.assertIn('Password:', response.content)
        self.assertIn('input type="password" name="password" value="" size="50"', response.content)

        #Submit button
        self.assertIn('input type="submit" name="submit" value="Log in"', response.content)

    def test_login_provide_error_message(self):
        # Access login page
        response = self.client.post('/rango/login/', {'username': 'wronguser', 'password': 'wrongpass'})

        self.assertIn('The username/password is incorrect. Please try again.', response.content)

    def test_login_redirects_to_index(self):
        # Create a user
        test_utils.create_user()

        # Access login page via POST with user data
        response = self.client.post('/rango/login/', {'username': 'testuser', 'password': 'test1234'})

        # Check it redirects to index
        self.assertRedirects(response, '/rango/')

    def test_upload_image(self):
        # Create fake user and image to upload to register user
        image = SimpleUploadedFile("testuser.jpg", "file_content", content_type="image/jpeg")
        response = self.client.post('/rango/register/',
                         {'username': 'testuser', 'password':'test1234',
                          'email':'testuser@testuser.com',
                          'website':'http://www.testuser.com',
                          'picture':image } )

        # Check user was successfully registered
        self.assertIn('thank you for registering!', response.content)
        user = User.objects.get(username='testuser')
        user_profile = UserProfile.objects.get(user=user)
        path_to_image = settings.MEDIA_ROOT + '/profile_images/testuser.jpg'

        # Check file was saved properly
        self.assertTrue(os.path.isfile(path_to_image))

        # Delete fake file created
        default_storage.delete(settings.MEDIA_ROOT + '/profile_images/testuser.jpg')


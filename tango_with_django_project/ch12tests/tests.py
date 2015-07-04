from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
import test_utils
from django.core.urlresolvers import reverse

class Chapter12LiveServerTests(StaticLiveServerTestCase):
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

        # password1
        password_field = self.browser.find_element_by_name('password1')
        password_field.send_keys('test1234')

        # password2
        password2_field = self.browser.find_element_by_name('password2')
        password2_field.send_keys('test1234')

        # Submit
        self.browser.find_element_by_name('submit').click()

        # Check if it is in the home page (redirected)
        self.assertEquals(self.browser.current_url, self.live_server_url + '/rango/')

    def test_login_and_logout(self):
        # Access login page
        self.browser.get(self.live_server_url + '/accounts/login/')

        # Log in
        test_utils.login(self)

        #Clicks to logout
        self.browser.find_element_by_link_text('Logout').click()

        # Check if it is in the home page
        self.assertEquals(self.browser.current_url, self.live_server_url + '/rango/')

    # TODO Is this test needed? Django implemented functionality
    # def test_password_change(self):
    #     # Access login page
    #     self.browser.get(self.live_server_url + '/accounts/login/')
    #
    #     # Log in
    #     test_utils.login(self)
    #
    #     # Check if it is in the home page
    #     self.assertEquals(self.browser.current_url, self.live_server_url + '/rango/')
    #
    #     # Access password change page
    #     self.browser.get(self.live_server_url + '/accounts/password/change/')
    #
    #     # Fill password change form
    #     # old_password
    #     password_field = self.browser.find_element_by_name('old_password')
    #     password_field.send_keys('admin')
    #
    #     # new_password1
    #     password_field = self.browser.find_element_by_name('new_password1')
    #     password_field.send_keys('admintest')
    #
    #     # new_password2
    #     password2_field = self.browser.find_element_by_name('new_password2')
    #     password2_field.send_keys('admintest')
    #
    #     # Check for password successfully changed message
    #     body = self.browser.find_element_by_tag_name('body')
    #     self.assertIn('Password change successful', body.text)

class Chapter12ViewTests(TestCase):

    def test_new_login_form_is_displayed_correctly(self):
        #Access login page
        response = self.client.get('/accounts/login/')

        #Check form display
        #Header
        self.assertIn('<h1>Login to Rango</h1>', response.content)

        #Username label and input text
        self.assertIn('Username:', response.content)
        self.assertIn('name="username" type="text"', response.content)

        #Password label and input text
        self.assertIn('Password:', response.content)
        self.assertIn('name="password" type="password"', response.content)

        #Submit button
        self.assertIn('input type="submit" value="Log in"', response.content)

        #Message for not members
        self.assertIn('Not a member? <a href="' + reverse('registration_register') + '">Register</a>!',
                      response.content)

    def test_new_registration_form_is_displayed_correctly(self):
        #Access registration page
        response = self.client.get('/accounts/register/')

        # Check if form is rendered correctly
        self.assertIn('<h1>Register with Rango</h1>', response.content)

        #Username label and input text
        self.assertIn('Username:', response.content)
        self.assertIn('name="username"', response.content)

        #Email label and input email
        self.assertIn('E-mail:', response.content)
        self.assertIn('name="email"', response.content)

        #Password label and input password
        self.assertIn('Password:', response.content)
        self.assertIn('name="password1"', response.content)

        #Password label and input password
        self.assertIn('Password confirmation:', response.content)
        self.assertIn('name="password2"', response.content)

        # Check submit button
        self.assertIn('type="submit"', response.content)

    def test_links_are_updated_in_base_template(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access index page
        response = self.client.get('/rango/')

        # Check links that appear for logged person only
        self.assertIn(reverse('auth_logout'), response.content)

        #Log out
        self.client.logout()

        #Access index page with user not logged
        response = self.client.get('/rango/')

        # Check links that appear for logged person only
        self.assertIn(reverse('registration_register'), response.content)
        self.assertIn(reverse('auth_login'), response.content)

    def test_previous_templates_are_not_used_anymore(self):
        # Access previous login url
        response = self.client.get('/rango/login/')
        self.assertEquals(response.status_code, 404)

        # Access previous register url
        response = self.client.get('/rango/register/')
        self.assertEquals(response.status_code, 404)

        # Access previous login url
        response = self.client.get('/rango/logout/')
        self.assertEquals(response.status_code, 404)

    # TODO Is this test needed? Django implemented functionality
    # def test_password_change_functionality(self):
    #     pass
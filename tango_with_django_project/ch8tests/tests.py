from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rango.forms import CategoryForm, PageForm
import test_utils
from rango.models import Category
from django.core.urlresolvers import reverse
from rango.decorators import chapter8

class Chapter8LiveServerTestCase(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    @chapter8
    def test_form_is_saving_new_category(self):
        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        categories_link[0].click()

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

    @chapter8
    def test_form_error_when_category_field_empty(self):
        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        categories_link[0].click()

        # Click on Create Category with name field empty
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if there is an error message
        self.assertIn('This field is required.', body.text)

    @chapter8
    def test_add_category_that_already_exists(self):
        # Create a category in database
        new_category = Category(name="New Category")
        new_category.save()

        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        # Check if is there link to add categories
        categories_link = self.browser.find_elements_by_partial_link_text('Add a New Category')
        categories_link[0].click()

        # Types new category name
        username_field = self.browser.find_element_by_name('name')
        username_field.send_keys('New Category')

        # Click on Create Category
        self.browser.find_element_by_css_selector(
            "input[type='submit']"
        ).click()

        body = self.browser.find_element_by_tag_name('body')

        # Check if there is an error message
        self.assertIn('Category with this Name already exists.', body.text)

    @chapter8
    def test_form_is_saving_new_page(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        i = 0

        for category in categories:
            i = i + 1
            # Access link to add page for the category
            self.browser.get(self.live_server_url + reverse('add_page', args=[category.slug]))

            # Types new page name
            username_field = self.browser.find_element_by_name('title')
            username_field.send_keys('New Page ' + str(i))

            # Types url for the page
            username_field = self.browser.find_element_by_name('url')
            username_field.send_keys('http://www.newpage1.com')

            # Click on Create Page
            self.browser.find_element_by_css_selector(
                "input[type='submit']"
            ).click()

            body = self.browser.find_element_by_tag_name('body')

            # Check if New Page appears in the category page
            self.assertIn('New Page', body.text)

    # def test_cleaned_data_from_add_page(self):
    #     #TODO HTML does not let put a not valid url due to type="url"
    #     #TODO so cleaned data is never called
    #     #Create categories and pages
    #     categories = test_utils.create_categories()
    #     i = 0
    #
    #     for category in categories:
    #         i = i + 1
    #         # Access link to add page for the category
    #         self.browser.get(self.live_server_url + '/rango/category/' + category.slug + '/add_page/')
    #
    #         # Types new page name
    #         username_field = self.browser.find_element_by_name('title')
    #         username_field.send_keys('New Page ' + str(i))
    #
    #         # Types url for the page
    #         username_field = self.browser.find_element_by_name('url')
    #         username_field.send_keys('newpage' + str(1) + '.com')
    #
    #         # Click on Create Page
    #         self.browser.find_element_by_css_selector(
    #             "input[type='submit']"
    #         ).click()
    #
    #         body = self.browser.find_element_by_tag_name('body')
    #
    #         # Check if New Page appears in the category page
    #         self.assertIn('New Page', body.text)

class Chapter8ViewTests(TestCase):
    @chapter8
    def test_index_contains_link_to_add_category(self):
        # Access index
        response = self.client.get(reverse('index'))

        # Check if there is text and a link to add category
        self.assertIn('Add a New Category', response.content)
        self.assertIn('href="' + reverse('add_category') + '"', response.content)

    @chapter8
    def test_add_category_form_is_displayed_correctly(self):
        # Access add category page
        response = self.client.get(reverse('add_category'))

        # Check form in response context is instance of CategoryForm
        self.assertTrue(isinstance(response.context['form'], CategoryForm))

        # Check form is displayed correctly
        # Header
        self.assertIn('<h1>Add a Category</h1>', response.content)

        # Label
        self.assertIn('Please enter the category name.', response.content)

        # Text input
        self.assertIn('id="id_name" maxlength="128" name="name" type="text"', response.content)

        # Button
        self.assertIn('type="submit" name="submit" value="Create Category"', response.content)

    @chapter8
    def test_add_page_form_is_displayed_correctly(self):
        # Create categories
        categories = test_utils.create_categories()

        for category in categories:
            # Access add category page
            response = self.client.get(reverse('add_page', args=[category.slug]))

            # Check form in response context is instance of CategoryForm
            self.assertTrue(isinstance(response.context['form'], PageForm))

            # Check form is displayed correctly

            # Label 1
            self.assertIn('Please enter the title of the page.', response.content)

            # Label 2
            self.assertIn('Please enter the URL of the page.', response.content)

            # Text input 1
            self.assertIn('id="id_title" maxlength="128" name="title" type="text"', response.content)

            # Text input 2
            self.assertIn('id="id_url" maxlength="200" name="url" type="url"', response.content)

            # Button
            self.assertIn('type="submit" name="submit" value="Create Page"', response.content)

    def test_access_category_that_does_not_exists(self):
        # Access a category that does not exist
        response = self.client.get(reverse('category', args=['python']))

        # Check that it has a response as status code OK is 200
        self.assertEquals(response.status_code, 200)

        # Check the rendered page is not empty, thus it was customised (I suppose)
        self.assertNotEquals(response.content, '')

    def test_link_to_add_page_only_appears_in_valid_categories(self):
        # Access a category that does not exist
        response = self.client.get(reverse('category', args=['python']))

        # Check that there is not a link to add page
        self.assertNotIn(reverse('add_page', args=['python']), response.content)

        # Access a category that does not exist
        response = self.client.get(reverse('category', args=['other-frameworks']))

        # Check that there is not a link to add page
        self.assertNotIn(reverse('add_page', args=['other-frameworks']), response.content)

    @chapter8
    def test_category_contains_link_to_add_page(self):
        # Crete categories
        categories = test_utils.create_categories()

        # For each category in the database check if contains link to add page
        for category in categories:
            response = self.client.get(reverse('category', args=[category.slug]))
            self.assertIn(reverse('add_page', args=[category.slug]), response.content)



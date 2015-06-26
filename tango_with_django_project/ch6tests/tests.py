from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from rango.models import Page, Category
import populate_rango
from selenium import webdriver
import test_utils

class Chapter6LiveServerTests(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_population_script(self):
        #Populate database
        populate_rango.populate()

        self.browser.get(self.live_server_url + '/admin/')

        # Log in the admin page
        test_utils.login(self)

        # Check if is there link to categories
        category_link = self.browser.find_elements_by_partial_link_text('Categor')
        category_link[0].click()

        # Check for the categories saved by the population script
        self.browser.find_elements_by_partial_link_text('Other Frameworks')
        self.browser.find_elements_by_partial_link_text('Django')
        self.browser.find_elements_by_partial_link_text('Python')

        # Check the pages saved by the population script
        self.browser.get(self.live_server_url + '/admin/rango/page/')
        self.browser.find_elements_by_partial_link_text('Flask')
        self.browser.find_elements_by_partial_link_text('Bottle')
        self.browser.find_elements_by_partial_link_text('How to Tango with Django')
        self.browser.find_elements_by_partial_link_text('Official Django Tutorial')
        self.browser.find_elements_by_partial_link_text('Django Rocks')
        self.browser.find_elements_by_partial_link_text('Learn Python in 10 Minutes')
        self.browser.find_elements_by_partial_link_text('How to Think like a Computer Scientist')
        self.browser.find_elements_by_partial_link_text('Official Python Tutorial')

    def test_admin_page_contains_title_url_and_category(self):
        #Populate database
        populate_rango.populate()

        self.browser.get(self.live_server_url + '/admin/')

        # Log in the admin page
        test_utils.login(self)

        # Click in Pages
        pages_link = self.browser.find_element_by_link_text('Pages')
        pages_link.click()

        body = self.browser.find_element_by_tag_name('body')

        # Get all pages
        pages = Page.objects.all()

        # Check all pages title, category and url are displayed
        for page in pages:
            self.assertIn(page.title, body.text)
            self.assertIn(page.category.name, body.text)
            self.assertIn(page.url, body.text)

        # Check for the Github account and PythonAnywhere account
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('pythonanywhere.com', body.text)
        self.assertIn('github.com', body.text)


    def test_can_create_new_category_via_admin_site(self):
        #Access admin page
        self.browser.get(self.live_server_url + '/admin/')

        # Check if it display admin message
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # Log in the admin page
        test_utils.login(self)

        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        # Check if is there link to categories
        category_link = self.browser.find_elements_by_partial_link_text('Categor')
        self.assertEquals(len(category_link), 1)

        # Click in the link
        category_link[0].click()

        # Empty, so check for the empty message
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('0 categor', body.text)

        # Add a category by clicking on 'Add category
        new_poll_link = self.browser.find_element_by_link_text('Add category')
        new_poll_link.click()

        # Check for input field
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Name:', body.text)

        # Input category name
        category_field = self.browser.find_element_by_name('name')
        category_field.send_keys("Test Driven Development")

        # Leave likes and views as 0

         # Gertrude clicks the save button
        save_button = self.browser.find_element_by_css_selector("input[value='Save']")
        save_button.click()

        # As redirected there is a link for the category
        category_link = self.browser.find_elements_by_link_text(
                "Test Driven Development"
        )
        self.assertEquals(len(category_link), 1)

class Chapter6ModelTests(TestCase):

    def test_create_a_new_category(self):
        cat = Category(name="Python")
        cat.save()

        # Check category is in database
        categories_in_database = Category.objects.all()
        self.assertEquals(len(categories_in_database), 1)
        only_poll_in_database = categories_in_database[0]
        self.assertEquals(only_poll_in_database, cat)

    def test_create_pages_for_categories(self):
        cat = Category(name="Python")
        cat.save()

        # create 2 pages for category python
        python_page = Page()
        python_page.category = cat
        python_page.title="Official Python Tutorial"
        python_page.url="http://docs.python.org/2/tutorial/"
        python_page.save()

        django_page = Page()
        django_page.category = cat
        django_page.title="Django"
        django_page.url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/"
        django_page.save()

        # Check if they both were saved
        python_pages = cat.page_set.all()
        self.assertEquals(python_pages.count(), 2)

        #Check if they were saved properly
        first_page = python_pages[0]
        self.assertEquals(first_page, python_page)
        self.assertEquals(first_page.title , "Official Python Tutorial")
        self.assertEquals(first_page.url, "http://docs.python.org/2/tutorial/")

    def test_population_script_changes(self):
        #Populate database
        populate_rango.populate()

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Python')
        self.assertEquals(cat.views, 128)
        self.assertEquals(cat.likes, 64)

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Django')
        self.assertEquals(cat.views, 64)
        self.assertEquals(cat.likes, 32)

        # Check if the category has correct number of views and likes
        cat = Category.objects.get(name='Other Frameworks')
        self.assertEquals(cat.views, 32)
        self.assertEquals(cat.likes, 16)
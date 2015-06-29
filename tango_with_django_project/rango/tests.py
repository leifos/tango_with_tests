from django.test import TestCase
import test_utils
from django.template import loader
from django.conf import settings
import os.path
from django.core.urlresolvers import reverse

class Chapter10ViewTests(TestCase):
    
    def test_base_template_exists(self):
        # Check base.html exists inside template folder
        path_to_base = settings.TEMPLATE_PATH + '/base.html'
        self.assertTrue(os.path.isfile(path_to_base))

    def test_titles_displayed(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()

        # Access index and check the title displayed
        response = self.client.get('/rango/')
        self.assertIn('<title>Rango - How to Tango with Django!</title>', response.content)

        # Access category page and check the title displayed
        response = self.client.get('/rango/category/' + categories[0].slug + '/')
        self.assertIn('<title>Rango - ' + categories[0].name + '</title>', response.content)

        # Access about page and check the title displayed
        response = self.client.get('/rango/about/')
        self.assertIn('<title>Rango - About</title>', response.content)

        # Access login page and check the title displayed
        response = self.client.get('/rango/login/')
        self.assertIn('<title>Rango - Login</title>', response.content)

        # Access register page and check the title displayed
        response = self.client.get('/rango/register/')
        self.assertIn('<title>Rango - Register</title>', response.content)

        # Access restricted page and check the title displayed
        response = self.client.get('/rango/restricted/')
        self.assertIn('<title>Rango - Restricted Page</title>', response.content)

        # Access add page and check the title displayed
        response = self.client.get('/rango/category/' + categories[0].slug + '/add_page/')
        self.assertIn('<title>Rango - Add Page</title>', response.content)

        # Access add new category page and check the title displayed
        response = self.client.get('/rango/add_category/')
        self.assertIn('<title>Rango - Add Category</title>', response.content)

    def test_templates_inherits_from_base_template(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()

        # Create a list of pages to access
        pages = ['/rango/', '/rango/about/', '/rango/add_category/', '/rango/register/', '/rango/login/',
                 '/rango/category/' + categories[0].slug + '/', '/rango/category/' + categories[0].slug + '/add_page/',
                 '/rango/restricted/']

        # For each page in the page list, check if it extends from base template
        for page in pages:
            response = self.client.get(page)
            base_html = loader.get_template('base.html')
            self.assertTrue(any(base_html.name == template.name for template in response.templates))

    def test_pages_using_templates(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()
        # Create a list of pages to access
        pages = ['/rango/', '/rango/about/', '/rango/add_category/', '/rango/register/', '/rango/login/',
                 '/rango/category/' + categories[0].slug + '/', '/rango/category/' + categories[0].slug + '/add_page/',
                 '/rango/restricted/']

        # Create a list of pages to access
        templates = ['rango/index.html', 'rango/about.html', 'rango/add_category.html', 'rango/register.html',
                     'rango/login.html','rango/category.html', 'rango/add_page.html', 'rango/restricted.html']

        # For each page in the page list, check if it extends from base template
        for template, page in zip(templates, pages):
            response = self.client.get(page)
            self.assertTemplateUsed(response, template)

    def test_url_reference_in_index_page_when_logged(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access index page
        response = self.client.get('/rango/')

        # Check links that appear for logged person only
        self.assertIn(reverse('add_category'), response.content)
        self.assertIn(reverse('restricted'), response.content)
        self.assertIn(reverse('logout'), response.content)
        self.assertIn(reverse('about'), response.content)

    def test_url_reference_in_index_page_when_not_logged(self):
        #Access index page with user not logged
        response = self.client.get('/rango/')

        # Check links that appear for logged person only
        self.assertIn(reverse('register'), response.content)
        self.assertIn(reverse('login'), response.content)
        self.assertIn(reverse('about'), response.content)

    def test_link_to_index_in_base_template(self):
        # Access index
        response = self.client.get('/rango/')

        # Check for url referencing index
        self.assertIn(reverse('index'), response.content)

    def test_url_reference_in_category_page(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        test_utils.create_categories()

        # Check for add_page in category page
        response = self.client.get('/rango/category/category-1/')
        self.assertIn(reverse('add_page', args=['category-1']), response.content)

    def test_link_to_home_in_about_page_no_longer_exists(self):
        # Access about page
        response = self.client.get('/rango/about/')

        # Check there is only one link to index
        self.assertEquals(response.content.count('href="' + reverse('index') + '"'), 1)





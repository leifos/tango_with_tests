from django.test import TestCase
import test_utils

class Chapter13ViewTests(TestCase):
    def test_base_uses_bootstrap_css(self):
        # Access index
        response = self.client.get('/rango/')
        self.assertIn('<link href="http://getbootstrap.com/dist/css/bootstrap.min.css" rel="stylesheet">',
                      response.content)
        self.assertIn('<link href="http://getbootstrap.com/examples/dashboard/dashboard.css" rel="stylesheet">',
                      response.content)

    def test_all_templates_contain_a_page_header(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()

        # Create a list of pages to access
        pages = ['/rango/', '/rango/about/', '/rango/add_category/', '/accounts/register/', '/accounts/login/',
                 '/rango/category/' + categories[0].slug + '/', '/rango/category/' + categories[0].slug + '/add_page/',
                 '/rango/restricted/']

        # For each page in the page list, check if it has a page header
        for page in pages:
            response = self.client.get(page)
            self.assertIn('<div class="page-header">', response.content)

    def test_list_item_in_index_are_presented_using_list_group(self):
        #Create categories and pages
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        #Access index page
        response = self.client.get('/rango/')

        #Check for usage of list-group
        self.assertIn('<ul class="list-group">', response.content)
        self.assertIn('<li class="list-group-item">', response.content)

    def test_headings_in_index_are_using_panel(self):
        #Access index
        response = self.client.get('/rango/')

        # Check panel use for categories
        self.assertIn('<div class="panel panel-primary">', response.content)
        self.assertIn('<div class="panel-heading">', response.content)
        self.assertIn('<h3 class="panel-title">', response.content)
        self.assertIn('Pages', response.content)
        self.assertIn('Categories', response.content)

    def test_login_page_is_bootstrapped(self):
        # Access login page
        response = self.client.get('/accounts/login/')

        # Check bootstrap CSS
        self.assertIn('<link href="http://getbootstrap.com/examples/signin/signin.css" rel="stylesheet">',
                      response.content)

    def test_add_category_is_bootstrapped(self):
        # Create user and login
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access add category page
        response = self.client.get('/rango/add_category/')

        #Check it uses bootstrap classes
        self.assertIn('<h2 class="form-signin-heading">', response.content)
        self.assertIn('<button class="btn btn-primary"', response.content)

    def test_add_page_is_bootstrapped(self):
        # Create user and login
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        test_utils.create_categories()

        # Access add category page
        response = self.client.get('/rango/category/category-1/add_page/')

        #Check it uses bootstrap classes
        self.assertIn('<h2 class="form-signin-heading">', response.content)
        self.assertIn('<button class="btn btn-primary"', response.content)

    def test_register_page_is_bootstrapped(self):
        # Access register page
        response = self.client.get('/accounts/register/')

        #Check for bootstrap use
        self.assertIn('<h2 class="form-signin-heading"', response.content)
        self.assertIn('<div class="form-group">', response.content)
        self.assertIn('<p class="required">', response.content)
        self.assertIn('<input class="form-control', response.content)
        self.assertIn('class="btn btn-default"', response.content)
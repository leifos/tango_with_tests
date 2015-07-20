from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import test_utils
from rango.models import Category, Page
from selenium import webdriver
import populate_rango
from rango.decorators import chapter7

from django.core.urlresolvers import reverse
class Chapter7ModelTests(TestCase):
    def test_category_contains_slug_field(self):
        #Create a new category
        new_category = Category(name="Test Category")
        new_category.save()

        #Check slug was generated
        self.assertEquals(new_category.slug, "test-category")

        #Check there is only one category
        categories = Category.objects.all()
        self.assertEquals(len(categories), 1)

        #Check attributes were saved correctly
        categories[0].slug = new_category.slug

class Chapter7ViewTests(TestCase):
    def test_index_context(self):
        # Access index with empty database
        response = self.client.get(reverse('index'))

        # Context dictionary is then empty
        self.assertItemsEqual(response.context['categories'], [])
        self.assertItemsEqual(response.context['pages'], [])

        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        #Access index with database filled
        response = self.client.get(reverse('index'))

        #Retrieve categories and pages from database
        categories = Category.objects.order_by('-likes')[:5]
        pages = Page.objects.order_by('-views')[:5]

        # Check context dictionary filled
        self.assertItemsEqual(response.context['categories'], categories)
        self.assertItemsEqual(response.context['pages'], pages)

    def test_index_displays_five_most_liked_categories(self):
        #Create categories
        test_utils.create_categories()

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most likes are displayed
        for i in xrange(10, 5, -1):
            self.assertIn("Category " + str(i), response.content)

    def test_index_displays_no_categories_message(self):
        # Access index with empty database
        response = self.client.get(reverse('index'))

        # Check if no categories message is displayed
        self.assertIn("There are no categories present.", response.content)

    def test_index_displays_five_most_viewed_pages(self):
        #Create categories
        categories = test_utils.create_categories()

        #Create pages for categories
        test_utils.create_pages(categories)

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most views are displayed
        for i in xrange(20, 15, -1):
            self.assertIn("Page " + str(i), response.content)


    def test_index_contains_link_to_categories(self):
        #Create categories
        categories = test_utils.create_categories()

        # Access index
        response = self.client.get(reverse('index'))

        # Check if the 5 pages with most likes are displayed
        for i in xrange(10, 5, -1):
            category = categories[i - 1]
            self.assertIn(reverse('category', args=[category.slug]), response.content)

    def test_category_context(self):
        #Create categories and pages for categories
        categories = test_utils.create_categories()
        test_utils.create_pages(categories)

        # For each category check the context dictionary passed via render() function
        for category in categories:
            response = self.client.get(reverse('category', args=[category.slug]))
            pages = Page.objects.filter(category=category)
            self.assertEquals(response.context['category_name'], category.name)
            self.assertItemsEqual(response.context['pages'], pages)
            self.assertEquals(response.context['category'], category)

    def test_category_page_using_template(self):
        #Create categories in database
        test_utils.create_categories()

        # Access category page
        response = self.client.get(reverse('category', args=['category-1']))

        # check was used the right template
        self.assertTemplateUsed(response, 'rango/category.html')

    @chapter7
    def test_category_page_displays_pages(self):
        #Create categories in database
        categories = test_utils.create_categories()

        # Create pages for categories
        test_utils.create_pages(categories)

        # For each category, access its page and check for the pages associated with it
        for category in categories:
            # Access category page
            response = self.client.get(reverse('category', args=[category.slug]))

            # Retrieve pages for that category
            pages = Page.objects.filter(category=category)

            # Check pages are displayed and they have a link
            for page in pages:
                self.assertIn(page.title, response.content)
                self.assertIn(page.url, response.content)

    def test_category_page_displays_empty_message(self):
        #Create categories in database
        categories = test_utils.create_categories()

        # For each category, access its page and check there are no pages associated with it
        for category in categories:
            # Access category page
            response = self.client.get(reverse('category', args=[category.slug]))
            self.assertIn("No pages currently in category.", response.content)

    def test_category_page_displays_category_does_not_exist_message(self):
        # Try to access categories not saved to database and check the message
        response = self.client.get(reverse('category', args=['Python']))
        # self.assertIn("The specified category  does not exist!", response.content)
        self.assertIn("does not exist!", response.content)

        response = self.client.get(reverse('category', args=['Django']))
        # self.assertIn("The specified category  does not exist!", response.content)
        self.assertIn("does not exist!", response.content)

class Chapter7LiveServerTests(StaticLiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_category_on_admin_page_contains_slug_field(self):
        # Populate database
        populate_rango.populate()

        # Access admin page
        self.browser.get(self.live_server_url + reverse('admin:index'))

        # Log in the admin page
        test_utils.login(self)

        # Check if is there link to categories
        categories_link = self.browser.find_elements_by_partial_link_text('Categor')
        categories_link[0].click()

        # Check for the categories saved by the population script
        category_link = self.browser.find_elements_by_partial_link_text('Other Frameworks')
        category_link[0].click()

        body = self.browser.find_element_by_tag_name('body')

        # Check the slug field
        self.assertIn("Slug:", body.text)
        slug_input = self.browser.find_element_by_name("slug")
        self.assertEquals(slug_input.get_attribute("value"), "other-frameworks")

    def test_category_redirect_to_desired_page(self):
        # Populate database
        populate_rango.populate()

        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        #Access Python category page
        category_link = self.browser.find_elements_by_link_text('Python')
        category_link[0].click()

        # Check it is in the correct page
        self.assertEquals(self.browser.current_url, self.live_server_url + reverse('category', args=['python']))


        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        #Access Django category page
        category_link = self.browser.find_elements_by_link_text('Django')
        category_link[0].click()

        # Check it is in the correct page
        self.assertEquals(self.browser.current_url, self.live_server_url + reverse('category', args=['django']))

        # Access index page
        self.browser.get(self.live_server_url + reverse('index'))

        #Access Other Frameworks category page
        category_link = self.browser.find_elements_by_link_text('Other Frameworks')
        category_link[0].click()

        # Check it is in the correct page
        self.assertEquals(self.browser.current_url, self.live_server_url + reverse('category', args=['other-frameworks']))
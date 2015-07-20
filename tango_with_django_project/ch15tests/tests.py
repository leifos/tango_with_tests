from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from rango.decorators import chapter15

# Create your tests here.
class Chapter15ViewTests(TestCase):
    @chapter15
    def test_search_uses_template(self):
        #Access search page
        response = self.client.get(reverse('search'))

        #Assert it uses search template
        self.assertTemplateUsed(response, 'rango/search.html')

    @chapter15
    def test_search_form_is_displayed_correctly(self):
        #Access search page
        response = self.client.get(reverse('search'))

        # Check form display
        self.assertContains(response, '<input class="form-control" type="text" size="50" name="query"    '
                                      'value="" id="query" />', html=True)

        self.assertContains(response, '<input class="btn btn-primary"'
                                      ' type="submit" name="submit" value="Search" />', html=True)

    @chapter15
    def test_search_url_mapping(self):
        #Access search page
        response = self.client.get(reverse('search'))

        # Check that the rendered page was the search.html
        self.assertEquals(response.request['PATH_INFO'], reverse('search'))

    @chapter15
    def test_nav_bar_contains_link_to_search(self):
        #Access index page
        response = self.client.get(reverse('index'))

        #Check it has a link to search
        self.assertContains(response, reverse('search'))

    @chapter15
    def test_result_list(self):
        #Send search data via post
        response = self.client.post(reverse('search'), {'query':'Django'})

        # Get the result list
        result_list = response.context['result_list']

        # Assert there are 10 results displayed
        self.assertEquals(len(result_list), 10)

        # Check it has Django in the
        for result in result_list:
            self.assertIn('Django', result['title'])
            self.assertIsNotNone(result['link'])
            self.assertIsNotNone(result['summary'])

class Chapter15LiveServerTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    @chapter15
    def test_users_search(self):
        #Access index
        self.browser.get(self.live_server_url + reverse('index'))

        #Click search
        search_link = self.browser.find_element_by_link_text('Search')
        search_link.click()

        # Types and click search
        search_field = self.browser.find_element_by_name('query')
        search_field.send_keys('Django')
        search_button = self.browser.find_element_by_name('submit')
        search_button.click()

        # Assert there will be a result heading
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Results', body_text)

        # Assert there are 10 results displayed
        result_items = self.browser.find_elements_by_class_name("list-group-item")
        self.assertEquals(len(result_items), 10)




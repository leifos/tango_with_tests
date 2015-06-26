from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.contrib.staticfiles import finders

class Chapter5ViewTest(TestCase):

    def test_view_has_title(self):
        response = self.client.get('/rango/')

        #Check title used correctly
        self.assertIn('<title>Rango</title>', response.content)

    def test_index_using_template(self):
        response = self.client.get('/rango/')

        # Check the template used to render index page
        self.assertTemplateUsed(response, 'rango/index.html')

    def test_about_using_template(self):
        response = self.client.get('/rango/about/')

        # Check the template used to render about page
        self.assertTemplateUsed(response, 'rango/about.html')

    def test_rango_picture_displayed(self):
        response = self.client.get('/rango/')

        # Check if is there an image in index page
        self.assertIn('img src="/static/images/rango.jpg', response.content)

    def test_about_contain_image(self):
        response = self.client.get('/rango/about/')

        # Check if is there an image in index page
        self.assertIn('img src="/static/images/', response.content)

    def test_serving_static_files(self):
        # If using static media properly result is not NONE once it finds rango.jpg
        result = finders.find('images/rango.jpg')
        self.assertIsNotNone(result)
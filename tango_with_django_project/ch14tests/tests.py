from django.test import TestCase
import test_utils
from django.template import Context, Template
from rango.models import Category
from django.core.urlresolvers import reverse

# Create your tests here.
class Chapter14ViewTests(TestCase):
    def test_template_tags(self):
        #Create categories
        categories = test_utils.create_categories()

        #Create template and context
        template = Template('{% load rango_extras %} {% get_category_list category %}')
        context = Context({'category': Category.objects.get(pk=1)})
        rendered = template.render(context)

        # If template tags are working, then it is possible to see all categories
        for category in categories:
            self.assertIn(category.slug, rendered)
            self.assertIn(category.name, rendered)


    def test_template_uses_sidebar(self):
        # Create some categories
        test_utils.create_categories()

        #Access index
        response = self.client.get(reverse('index'))

        #Check for sidebar class
        self.assertContains(response, 'class="col-sm-3 col-md-2 sidebar"')

        # Check it uses sidebar class when there are some categories
        self.assertContains(response, 'class="nav nav-sidebar"')

    def test_active_category_is_highlighted(self):
        # Create some categories
        categories = test_utils.create_categories()

        #Access each category and check whether it is the active category
        for category in categories:
            response = self.client.get(reverse('category', args=[category.slug]))
            self.assertContains(response, ' <li  class="active" > <a href="'
                                + reverse('category', args=[category.slug]) + '">'
                                + category.name + '</a></li>', count=1, html=True)

    def test_no_category_message_is_displayed_in_sidebar(self):
        #Access index page
        response = self.client.get(reverse('index'))

        # Check if no categories message is displayed in sidebar
        self.assertContains(response, 'There are no category present.')


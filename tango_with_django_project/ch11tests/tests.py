from django.test import TestCase
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse

# Create your tests here.
class Chapter11SessionTests(TestCase):
    def test_user_number_of_access_and_last_access_to_index(self):
        #Access index page 100 times
        for i in xrange(0, 100):
            self.client.get(reverse('index'))
            session = self.client.session

            # Check it exists visits and last_visit attributes on session
            self.assertIsNotNone(self.client.session['visits'])
            self.assertIsNotNone(self.client.session['last_visit'])

            # Check last visit time is within 0.1 second interval from now
            self.assertAlmostEqual(datetime.now(),
                datetime.strptime(session['last_visit'], "%Y-%m-%d %H:%M:%S.%f"), delta=timedelta(seconds=0.1))

            # Get last visit time subtracted by one day
            last_visit = datetime.now() - timedelta(days=1)

            # Set last visit to a day ago and save
            session['last_visit'] = str(last_visit)
            session.save()

            # Check if the visits number in session is being incremented and it's correct
            self.assertEquals(session['visits'], i + 1)

class Chapter11ViewTests(TestCase):
    def test_index_shows_number_of_visits(self):
        #Access index
        response = self.client.get(reverse('index'))

        # Check it contains visits message
        self.assertIn('visits: 1', response.content)

    def test_about_page_shows_number_of_visits(self):
        #Access index page to count one visit
        self.client.get(reverse('index'))

        # Access about page
        response = self.client.get(reverse('about'))

        # Check it contains visits message
        self.assertIn('visits: 1', response.content)

    def test_visit_number_is_passed_via_context(self):
        #Access index
        response = self.client.get(reverse('index'))

        # Check it contains visits message in the context
        self.assertIn('visits', response.context)

        #Access about page
        response = self.client.get(reverse('about'))

        # Check it contains visits message in the context
        self.assertIn('visits', response.context)



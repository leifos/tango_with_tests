from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from polls.models import Question, Choice
from polls.test_utils import create_question

class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        response = self.client.get(reverse('polls:detail',
                                   args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        response = self.client.get(reverse('polls:detail',
                                   args=(past_question.id,)))
        self.assertContains(response, past_question.question_text,
                            status_code=200)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class HomePageViewTest(TestCase):

    def test_root_url_shows_links_to_all_polls(self):
        # set up some polls
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Question(question_text='life, the universe and everything', pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/polls/')
        # check we've used the right template
        self.assertTemplateUsed(response, 'polls/index.html')

        # check we've passed the polls to the template
        polls_in_context = response.context['latest_question_list']

        #As it orders by the most recent first, change the order to test -> poll2, poll1
        self.assertEquals(list(polls_in_context), [poll2, poll1])

        # check the poll names appear on the page
        self.assertIn(poll1.question_text, response.content)
        self.assertIn(poll2.question_text, response.content)

        # check the page also contains the urls to individual polls pages
        poll1_url = reverse('polls:detail', args=[poll1.id,])
        self.assertIn(poll1_url, response.content)
        poll2_url = reverse('polls:detail', args=[poll2.id,])
        self.assertIn(poll2_url, response.content)

class SinglePollViewTest(TestCase):

    def test_page_shows_poll_title_and_no_votes_message(self):
        # set up two polls, to check the right one is displayed
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Question(question_text='life, the universe and everything', pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/polls/%d/' % (poll2.id, ))

        # check we've used the poll template
        self.assertTemplateUsed(response, 'polls/detail.html')

        # check we've passed the right poll into the context
        self.assertEquals(response.context['question'], poll2)

        # check the poll's question appears on the page
        self.assertIn(poll2.question_text, response.content)

        # check our 'no votes yet' message appears
        # self.assertIn('No-one has voted on this poll yet', response.content)

    def test_page_shows_choices_using_form(self):
        # set up a poll with choices
        poll1 = Question(question_text='time', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(question=poll1, choice_text="PM", votes=0)
        choice1.save()
        choice2 = Choice(question=poll1, choice_text="Gardener's", votes=0)
        choice2.save()

        response = self.client.get('/polls/%d/' % (poll1.id, ))

        # check we've passed in a form of the right type
        #Not in the Django official tutorial
        #self.assertTrue(isinstance(response.context['form'], QuestionVoteForm))

        # and check the form is being used in the template,
        # by checking for the choice text
        self.assertIn(choice1.choice_text, response.content.replace('&#39;', "'"))
        self.assertIn(choice2.choice_text, response.content.replace('&#39;', "'"))

    def test_view_can_handle_votes_via_POST(self):
        # set up a poll with choices
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(question=poll1, choice_text='42', votes=1)
        choice1.save()
        choice2 = Choice(question=poll1, choice_text='The Ultimate Answer', votes=3)
        choice2.save()

        # set up our POST data - keys and values are strings
        post_data = {'choice': str(choice2.id)}

        # make our request to the view
        poll_url = '/polls/%d/vote/' % (poll1.id,)
        response = self.client.post(poll_url, data=post_data)

        #URL to redirect
        redirect_url = '/polls/%d/results/' % (poll1.id,)

        # retrieve the updated choice from the database
        choice_in_db = Choice.objects.get(pk=choice2.id)

        # check it's votes have gone up by 1
        self.assertEquals(choice_in_db.votes, 4)

        # always redirect after a POST - even if, in this case, we go back
        # to the same page.
        self.assertRedirects(response, redirect_url)

    def test_view_shows_percentage_of_votes(self):
        # set up a poll with choices
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(question=poll1, choice_text='42', votes=1)
        choice1.save()
        choice2 = Choice(question=poll1, choice_text='The Ultimate Answer', votes=2)
        choice2.save()

        response = self.client.get('/polls/%d/results/' % (poll1.id, ))

        # check the percentages of votes are shown, sensibly rounded
        self.assertIn('33 %: 42', response.content)
        self.assertIn('67 %: The Ultimate Answer', response.content)

        # and that the 'no-one has voted' message is gone
        #self.assertNotIn('No-one has voted', response.content)

    def test_choice_can_calculate_its_own_percentage_of_votes(self):
        poll = Question(question_text='who?', pub_date=timezone.now())
        poll.save()
        choice1 = Choice(question=poll,choice_text='me',votes=2)
        choice1.save()
        choice2 = Choice(question=poll,choice_text='you',votes=1)
        choice2.save()

        self.assertEquals(choice1.percentage(), 100 * 2 / 3.0)
        self.assertEquals(choice2.percentage(), 100 * 1 / 3.0)

        # also check 0-votes case
        choice1.votes = 0
        choice1.save()
        choice2.votes = 0
        choice2.save()
        self.assertEquals(choice1.percentage(), 0)
        self.assertEquals(choice2.percentage(), 0)

    def test_view_shows_total_votes(self):
        # set up a poll with choices
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(question=poll1, choice_text='42', votes=1)
        choice1.save()
        choice2 = Choice(question=poll1, choice_text='The Ultimate Answer', votes=2)
        choice2.save()

        response = self.client.get('/polls/%d/results/' % (poll1.id, ))
        self.assertIn('3 votes', response.content)

        # also check we only pluralise "votes" if necessary. details!
        choice2.votes = 0
        choice2.save()
        response = self.client.get('/polls/%d/results/' % (poll1.id, ))
        self.assertIn('1 vote', response.content)
        self.assertNotIn('1 votes', response.content)
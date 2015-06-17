import datetime

from forms import QuestionVoteForm
from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from polls.models import Question, Choice
from polls.test_utils import create_question

class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


    def test_creating_a_new_poll_and_saving_it_to_the_database(self):
        # start by creating a new Poll object with its "question" set
        poll = Question()
        poll.question_text = "What's up?"
        poll.pub_date = timezone.now()

        # check we can save it to the database
        poll.save()

        # now check we can find it in the database again
        all_polls_in_database = Question.objects.all()
        self.assertEquals(len(all_polls_in_database), 1)
        only_poll_in_database = all_polls_in_database[0]
        self.assertEquals(only_poll_in_database, poll)

        # and check that it's saved its two attributes: question and pub_date
        self.assertEquals(only_poll_in_database.question_text, "What's up?")
        self.assertEquals(only_poll_in_database.pub_date, poll.pub_date)

    def test_verbose_name_for_pub_date(self):
        for field in Question._meta.fields:
            if field.name ==  'pub_date':
                self.assertEquals(field.verbose_name, 'Date published')

    def test_poll_objects_are_named_after_their_question(self):
        p = Question()
        p.question_text = 'How is babby formed?'
        self.assertEquals(unicode(p), 'How is babby formed?')


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

class ChoiceModelTest(TestCase):

    def test_creating_some_choices_for_a_poll(self):
        # start by creating a new Poll object
        poll = Question()
        poll.question_text="What's up?"
        poll.pub_date = timezone.now()
        poll.save()

        # now create a Choice object
        choice = Choice()

        # link it with our Poll
        choice.question = poll

        # give it some text
        choice.choice_text = "doin' fine..."

        # and let's say it's had some votes
        choice.votes = 3

        # save it
        choice.save()

        # try retrieving it from the database, using the poll object's reverse
        # lookup
        poll_choices = poll.choice_set.all()
        self.assertEquals(poll_choices.count(), 1)

        # finally, check its attributes have been saved
        choice_from_db = poll_choices[0]
        self.assertEquals(choice_from_db, choice)
        self.assertEquals(choice_from_db.choice_text, "doin' fine...")
        self.assertEquals(choice_from_db.votes, 3)

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

class PollsVoteFormTest(TestCase):

    def test_form_renders_poll_choices_as_radio_inputs(self):
        # set up a poll with a couple of choices
        poll1 = Question(question_text='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(question=poll1, choice_text='42', votes=0)
        choice1.save()
        choice2 = Choice(question=poll1, choice_text='The Ultimate Answer', votes=0)
        choice2.save()

        # set up another poll to make sure we only see the right choices
        poll2 = Question(question_text='time', pub_date=timezone.now())
        poll2.save()
        choice3 = Choice(question=poll2, choice_text='PM', votes=0)
        choice3.save()

        # build a voting form for poll1
        form = QuestionVoteForm(poll=poll1)

        # check it has a single field called 'vote', which has right choices:
        self.assertEquals(form.fields.keys(), ['vote'])

        # choices are tuples in the format (choice_number, choice_text):
        self.assertEquals(form.fields['vote'].choices, [
            (choice1.id, choice1.choice_text),
            (choice2.id, choice2.choice_text),
        ])

        # check it uses radio inputs to render
        self.assertIn('type="radio"', form.as_p())


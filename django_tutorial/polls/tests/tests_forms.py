from polls.forms import QuestionVoteForm
from django.utils import timezone
from django.test import TestCase
from polls.models import Question, Choice

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


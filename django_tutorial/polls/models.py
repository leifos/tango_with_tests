from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(verbose_name='Date published')

    def __unicode__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def total_votes(self):
        return sum(c.votes for c in self.choice_set.all())

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def percentage(self):
        total_votes_on_poll = sum(c.votes for c in self.question.choice_set.all())
        try:
            return 100.0 * self.votes / total_votes_on_poll
        except ZeroDivisionError:
            return 0

    def __unicode__(self):              # __unicode__ on Python 2
        return self.choice_text
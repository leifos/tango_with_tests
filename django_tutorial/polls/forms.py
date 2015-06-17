from django import forms


#Created for testing purposes only
class QuestionVoteForm(forms.Form):
    vote = forms.ChoiceField(widget=forms.RadioSelect())

    def __init__(self, poll):
        forms.Form.__init__(self)
        self.fields['vote'].choices = [(c.id, c.choice_text) for c in poll.choice_set.all()]
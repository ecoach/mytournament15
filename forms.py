from django import forms
from mycoach3 import settings
from datetime import datetime
from time import ctime
from django.shortcuts import redirect

class Voter_Form(forms.Form):
    vote = forms.ChoiceField(widget=forms.RadioSelect, choices=(('0', 'Test run',), ('1', 'Commit',)), initial=0)

    def __init__(self, vote_choices, *args, **kwargs):
        super(Voter_Form, self).__init__(*args, **kwargs)
        self.fields['vote'].choices = vote_choices 


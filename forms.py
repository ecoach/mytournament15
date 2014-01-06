from django import forms
from .models import *

# participation forms

class Register_Form(forms.Form):
    game = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder':"Paste your game...", 'class':'input-xxlarge'}))

class Voter_Form(forms.Form):
    vote = forms.ChoiceField(widget=forms.RadioSelect, choices=(('0', 'Test run',), ('1', 'Commit',)), initial=0)
    bout = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, vote_choices, *args, **kwargs):
        super(Voter_Form, self).__init__(*args, **kwargs)
        self.fields['vote'].choices = vote_choices 

# management forms

class New_Bracket_Form(forms.ModelForm):

    class Meta:
        model = Bracket
        fields = ['name', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder':"tourney name", 'class':'input-xxlarge'}),
        }

class Select_Bracket_Form(forms.Form):
    bracket = forms.ModelChoiceField(required=True, label='Select a Bracket', queryset=Bracket.objects.all().order_by('-id'), widget=forms.Select(attrs={'onchange': "$('#theform').submit();"}))

class Edit_Bracket_Form(forms.ModelForm):

    class Meta:
        model = Bracket
        fields = ['ready', 'finished']

class Pdf_Register_Form(forms.Form):
    game_file = forms.FileField(label='Select a file', required=True)



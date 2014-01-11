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
            'name': forms.TextInput(attrs={'placeholder':"bracket name", 'class':'input-xxlarge'}),
        }

class Select_Bracket_Form(forms.Form):
    bracket = forms.ModelChoiceField(required=True, label='Select a Bracket', queryset=Bracket.objects.all().order_by('-id'), widget=forms.Select(attrs={'onchange': "$('#theform').submit();"}))

class Edit_Bracket_Form(forms.ModelForm):
    trigger = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(attrs={'checked' : 'checked'}), choices=(('trigger', "Promote everyone on roster to competing and judging while activating tournament"),))

    class Meta:
        model = Bracket
        fields = ['status', 'name']

class Pdf_Register_Form(forms.Form):
    game_file = forms.FileField(label='Upload a pdf file', required=True)

class Roster_Csv_Form(forms.Form):
    roster_file = forms.FileField(label='Load list to use as roster', required=True)

class Competing_Csv_Form(forms.Form):
    game_file = forms.FileField(label='Load list to mark as competing', required=True)

class Competitor_Form(forms.ModelForm):

    class Meta:
        model = Competitor
        fields = ['status']

    def comp_name(self):
        mod = self.instance
        return mod.name

class Import_Judges_Form(forms.Form):
    trigger = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=(('trigger', "Import competitors as judges"),))


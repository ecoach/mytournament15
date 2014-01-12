from django import forms
from .models import *

# participation forms

class Register_Form(forms.Form):
    game = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder':"Paste your game...", 'class':'input-xxlarge'}))

BALLOT_CHOICES = (('A', 'Vote for A',), ('B', 'Vote for B',))
class Voter_Form(forms.ModelForm):
    ballot = forms.ChoiceField(required=False, label='', widget=forms.RadioSelect(), choices=BALLOT_CHOICES)

    class Meta:
        model = Bout
        fields = ['feedbackA', 'feedbackB']

        widgets = {
            'feedbackA': forms.Textarea(attrs={'placeholder':"See feedback instructions...", 'rows':20}),
            'feedbackB': forms.Textarea(attrs={'placeholder':"See feedback instructions...", 'rows':20}),
        }

    def clean_ballot(self):
        ballot = self.cleaned_data['ballot']
        if len(ballot) == 0:
            raise forms.ValidationError(self.fields['ballot'].error_messages['invalid'])
        return ballot

    def __init__(self, *args, **kwargs):
        super(Voter_Form, self).__init__(*args, **kwargs)
        self.fields['feedbackA'].label = 'Feedback on A:'
        self.fields['feedbackB'].label = 'Feedback on B:'

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
    trigger = forms.MultipleChoiceField(required=False, label='One click activation', widget=forms.CheckboxSelectMultiple(attrs={}), choices=(('trigger', "Activate bracket for voting and promote everyone on roster to competing and judging"),))

    class Meta:
        model = Bracket
        fields = ['name', 'prompt', 'status']

        widgets = {
            'prompt': forms.Textarea(attrs={'placeholder':"Voting instructions...", 'class':'input-xxlarge'}),
        }
    """
    def __init__(self, *args, **kwargs):
        super(Edit_Bracket_Form, self).__init__(*args, **kwargs)
        self.fields['prompt'].label = ':'
    """



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


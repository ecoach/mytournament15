from django import forms
from .models import *

# participation forms

class Register_Form(forms.Form):
    game = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder':"Paste your game...", 'class':'input-xxlarge'}))

BALLOT_CHOICES = (('A', 'Vote for A',), ('B', 'Vote for B',))
class Voter_Form(forms.ModelForm):
    ballot = forms.ChoiceField(required=False, label='', widget=forms.RadioSelect(), choices=BALLOT_CHOICES)
    boutid = forms.CharField(required=True, max_length=100, widget=forms.HiddenInput())

    class Meta:
        model = Bout
        fields = ['feedbackA', 'feedbackB', 'boutid']

        widgets = {
            'feedbackA': forms.Textarea(attrs={'placeholder':"See feedback instructions...", 'rows':20}),
            'feedbackB': forms.Textarea(attrs={'placeholder':"See feedback instructions...", 'rows':20}),
        }

    def __init__(self, *args, **kwargs):
        super(Voter_Form, self).__init__(*args, **kwargs)
        self.fields['feedbackA'].label = 'Feedback on A:'
        self.fields['feedbackB'].label = 'Feedback on B:'

    def clean_ballot(self):
        ballot = self.cleaned_data['ballot']
        if len(ballot) == 0:
            raise forms.ValidationError('Error: Step 4 - must select choice')
        return ballot

    def clean_feedbackA(self):
        bout = Bout.objects.get(pk=self.data['boutid'])
        feedbackA = self.cleaned_data['feedbackA']
        if bout.bracket.feedback_option == 'Required' and len(feedbackA) == 0:
            raise forms.ValidationError('Error: Step 2 - must provide some feedback')
        return feedbackA

    def clean_feedbackB(self):
        bout = Bout.objects.get(pk=self.data['boutid'])
        feedbackB = self.cleaned_data['feedbackB']
        if bout.bracket.feedback_option == 'Required' and len(feedbackB) == 0:
            raise forms.ValidationError('Error: Step 3 - must provide some feedback')
        return feedbackB

# management forms

class New_Bracket_Form(forms.ModelForm):

    class Meta:
        model = Bracket
        fields = ['name', 'manager', 'feedback_option']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder':"bracket name", 'class':'input-xxlarge'}),
        }

class Select_Bracket_Form(forms.Form):
    bracket = forms.ModelChoiceField(required=True, label='Select a Bracket', queryset=Bracket.objects.all().order_by('-id'), widget=forms.Select(attrs={'onchange': "$('#theform').submit();"}))

class Clone_Bracket_Form(forms.Form):
    triggers_bracket = forms.ChoiceField(
        required=True, 
        label='Bracket', 
        widget=forms.RadioSelect(attrs={}), 
        choices=(
            ('Open', "Clone bracket setting status to 'Open'"),
            ('Active', "Clone bracket setting status to 'Active'"),
        ),
        initial='Active',
        error_messages={'required': 'You must clone the bracket somehow'}
    )
    triggers_judges = forms.ChoiceField(
        required=True, 
        label='Judges', 
        widget=forms.RadioSelect(attrs={}), 
        choices=(
            ('without', "Clone without judges"),
            ('with', "Clone with judges setting decisions to zero"),
        ),
        initial='with',
        error_messages={'required': 'You must decide what to do about judges'}
    )
    triggers_competitors = forms.ChoiceField(
        required=True, 
        label='Competitors', 
        widget=forms.RadioSelect(attrs={}), 
        choices=(
            ('without', "Clone without competitors"),
            ('with', "Clone with competitors setting wins, losses, etc to zero"),
        ),
        initial='with',
        error_messages={'required': 'You must decide what to do about competitors'}
    )

class Edit_Bracket_Form(forms.ModelForm):
    trigger = forms.MultipleChoiceField(required=False, label='One click activation', widget=forms.CheckboxSelectMultiple(attrs={}), choices=(('trigger', "If you have loaded a 'Roster' (tabs above) then you can activate bracket for voting and promote everyone on the roster to competing and judging"),))

    class Meta:
        model = Bracket
        fields = ['name', 'feedback_option', 'prompt', 'status']

        widgets = {
            'prompt': forms.Textarea(attrs={'placeholder':"Voting and feedback instructions...", 'class':'input-xxlarge'}),
            #'feedback_option': forms.Select(),
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


from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from mynav.nav import main_nav
from .models import *
from .forms import *

# Create your views here.
@staff_member_required
def load_brackets_view(request, **kwargs):
    # read bracket list from CSV file
    import csv
    file_path = settings.DIR_UPLOAD_DATA + 'tournaments/load_brackets.csv'
    with open(file_path, 'rb') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in infile:
            bracket = Bracket.objects.get_or_create(name=row[0])[0]
            bracket.manager=row[1]
            bracket.description=row[2]
            #bracket.description='Chem 130 - Exam Prep'
            bracket.save()
    return render(request, 'mytournament/load_brackets.html', {
        "main_nav": main_nav(request.user, 'student_linkback')
    })


@staff_member_required
def load_competitors_view(request, **kwargs):
    # read competitor list from CSV file
    import csv
    file_path = settings.DIR_UPLOAD_DATA + 'tournaments/load_competitors.csv'
    with open(file_path, 'rb') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='"')
        bracket_prefix = infile.next()[0]
        for row in infile:
            bracket = get_bracket(bracket_prefix+str(row[1]))
            # populate bracket_id, name, game
            # avoid duplicate names per bracket, update game as needed
            cc = Competitor.objects.get_or_create(bracket=bracket, name=row[0])[0]
            cc.game = row[2]
            cc.wins = 0
            cc.losses = 0
            cc.points = 0
            cc.byes = 0
            cc.status = -1
            cc.save() 
    return render(request, 'mytournament/load_competitors.html', {
        "main_nav": main_nav(request.user, 'student_linkback')
    })

@staff_member_required
def load_judges_view(request, **kwargs):
    # read judges list from CSV file
    import csv
    file_path = settings.DIR_UPLOAD_DATA + 'tournaments/load_judges.csv'
    with open(file_path, 'rb') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='"')
        bracket_prefix = infile.next()[0]
        for row in infile:
            bracket = get_bracket(bracket_prefix+str(row[1]))
            # populate the bracket_id, name, eligable 
            # avoid duplicate names per bracket, update eligable as needed
            cc = Judge.objects.get_or_create(bracket=bracket, name=row[0])[0]
            cc.eligable=row[2]
            cc.decisions=0
            cc.save() 
    return render(request, 'mytournament/load_judges.html', {
        "main_nav": main_nav(request.user, 'student_linkback')
    })

def tournament_selector_view(request):
    return render(request, 'mytournament/selector.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": "None" 
    })

def info_view(request, **kwargs):
    bname = kwargs["bracket"]
    bracket = get_bracket(bname)
    return render(request, 'mytournament/info.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": bracket.description 
    })

def register_view(request, **kwargs):
    bname = kwargs["bracket"]
    bracket = get_bracket(bname)
    # load the manager
    manager = eval(bracket.manager)(bracket=bracket)
    
    # handle the form
    if request.method == 'POST':
        form = Register_Form(
            data=request.POST,
        )
        if form.is_valid():
            game = form.cleaned_data['game']
            manager.Register(request.user.username, game)
    form = Register_Form(
        initial={
            'game': manager.Game(request.user)
        },
    )

    return render(request, 'mytournament/register.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": bracket.description,
        "form": form,
        'game': manager.Game(request.user)
    })

def vote_view(request, **kwargs):
    bname = kwargs["bracket"]
    bracket = get_bracket(bname)
    # load the manager
    manager = eval(bracket.manager)(bracket=bracket)
   
    # handle the form
    if request.method == 'POST':
        form = Voter_Form(
            data=request.POST,
            vote_choices = manager.Vote_Choices(who=request.user.username),
        )
        if form.is_valid():
            bout = form.cleaned_data['bout']
            decision = form.cleaned_data['vote']
            manager.Record_Vote(bout, request.user.username, decision)
    # run manager setup
    manager.Setup(request.user.username) 
    form = Voter_Form(
        initial={
            'bout': manager.Bout_Id(request.user.username)
        },
        vote_choices = manager.Vote_Choices(who=request.user.username)
    )
    return render(request, 'mytournament/vote.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": bracket.description,
        "form": form,
        "judge": manager.Get_Judge(request.user.username),
        "status": manager.Status(request.user.username),
        "winner": manager.GetWinner()
    })

def get_bracket(bname):
    # find/create the bracket
    brackets = Bracket.objects.filter(name=bname)
    if brackets.count() == 0:
        #import pdb; pdb.set_trace() 
        bracket = Bracket.objects.get_or_create(name='00')[0]
        bracket.manager='Top20'
        bracket.description='Example for testing'
        bracket.save()
    else:
        bracket = brackets[0] 
    return bracket



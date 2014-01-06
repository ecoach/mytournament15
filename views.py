from django.shortcuts import render_to_response, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
#from mynav.tourney_nav import *
from mynav.mycoach_nav import *
from .steps import steps_nav
from .models import *
from .forms import *

# Create your views here.
@staff_member_required
def staff_view(request, **kwargs):
    return render(request, 'mytournament/staff.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'new_bracket'),
    })

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
            bracket.save()
    return render(request, 'mytournament/load_brackets.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'load_brackets'),
    })


@staff_member_required
def load_competitors_view(request, **kwargs):
    # read competitor list from CSV file
    import csv
    file_path = settings.DIR_UPLOAD_DATA + 'tournaments/load_competitors.csv'
    with open(file_path, 'rb') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in infile:
            bracket = Bracket.objects.get_or_create(id=row[1])[0]
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
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'load_competitors'),
    })

@staff_member_required
def load_judges_view(request, **kwargs):
    # read judges list from CSV file
    import csv
    file_path = settings.DIR_UPLOAD_DATA + 'tournaments/load_judges.csv'
    with open(file_path, 'rb') as csvfile:
        infile = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in infile:
            bracket = Bracket.objects.get_or_create(id=row[1])[0]
            # populate the bracket_id, name, eligable 
            # avoid duplicate names per bracket, update eligable as needed
            cc = Judge.objects.get_or_create(bracket=bracket, name=row[0])[0]
            cc.eligable=row[2]
            cc.decisions=0
            cc.save() 
    return render(request, 'mytournament/load_judges.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'load_judges'),
    })

@staff_member_required
def new_bracket_view(request, **kwargs):
    if request.method == 'POST':
        new_bracket_form = New_Bracket_Form(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            print name
            bname = form.cleaned_data['description']
            print description
            bname = form.cleaned_data['manager']
            print manager
            bracket = Bracket(name=name, description=description, manager=manager)
            bracket.save()
    else:
        new_bracket_form = New_Bracket_Form()
    return render(request, 'mytournament/new_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'new_bracket'),
        'new_bracket_form': new_bracket_form,
    })

@staff_member_required
def manage_bracket_view(request, **kwargs):
    return render(request, 'mytournament/manage_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_bracket'),
    })

@staff_member_required
def manage_competitors_view(request, **kwargs):
    return render(request, 'mytournament/manage_competitors.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_competitors'),
    })

@staff_member_required
def manage_judges_view(request, **kwargs):
    return render(request, 'mytournament/manage_judges.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_judges'),
    })

@staff_member_required
def review_bracket_view(request, **kwargs):
    return render(request, 'mytournament/manage_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'review_bracket'),
    })

def tournament_selector_view(request):
    return render(request, 'mytournament/selector.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": "None" 
    })

def info_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
    return render(request, 'mytournament/info.html', {
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket.description 
    })

def register_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
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
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket.description,
        "form": form,
        'game': manager.Game(request.user)
    })

def vote_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
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
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket.description,
        "form": form,
        "judge": manager.Get_Judge(request.user.username),
        "status": manager.Status(request.user.username),
        "winner": manager.GetWinner()
    })

def get_bracket(bid):
    # find/create the bracket
    brackets = Bracket.objects.filter(name=bid)
    if brackets.count() == 0:
        return None
    return brackets[0] 



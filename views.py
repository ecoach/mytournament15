from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from mynav.nav import main_nav
import loader
from .managers import *
from .forms import *

# Create your views here.

def tournament_selector_view(request):

    return render(request, 'mytournament/selector.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
    })

def info_view(request, **kwargs):

    if kwargs["bracket"] == '00':
        bracket = loader.bracket_00()

    return render(request, 'mytournament/info.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"]
    })

@staff_member_required
def load_competitors_view(request, **kwargs):

    if kwargs["bracket"] == '00':
        loader.competitors_00()

    return render(request, 'mytournament/load_competitors.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"]
    })

@staff_member_required
def load_judges_view(request, **kwargs):

    if kwargs["bracket"] == '00':
        loader.judges_00()

    return render(request, 'mytournament/load_judges.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"]
    })

def vote_view(request, **kwargs):

    # load the manager
    if kwargs["bracket"] == '00':
        bracket = loader.bracket_00()
    manager = eval(bracket.manager)(bracket=bracket)
    
    # run manager setup
    manager.Setup(request.user.username) 

    # handle the form
    if request.method == 'POST':
        form = Voter_Form(
            data=request.POST
            vote_choices = manager.Vote_Choices(judge=request.user.username)
        )
        if form.is_valid():
            f_vote = form.cleaned_data['vote']
            manager.Record_Vote(request.user.username, f_vote)
    form = Voter_Form(
        initial={},
        vote_choices = manager.Vote_Choices(judge=request.user.username)
    )
    return render(request, 'mytournament/vote.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"],
        "form": form,
        "status": manager.Status()
    })



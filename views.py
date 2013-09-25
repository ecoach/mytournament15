from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from mynav.nav import main_nav
import loader
from .managers import *

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

    if kwargs["bracket"] == '00':
        bracket = loader.bracket_00()

    manager = eval(bracket.manager)()
    ballot = manager.get_ballot()

    return render(request, 'mytournament/vote.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"],
        "ballot": ballot
    })



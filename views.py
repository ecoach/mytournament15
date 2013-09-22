from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from mynav.nav import main_nav

# Create your views here.

def tournament_selector_view(request):

    return render(request, 'mytournament/selector.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
    })

def info00_view(request, **kwargs):

    return render(request, 'mytournament/info00.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"]
    })

def vote00_view(request, **kwargs):

    return render(request, 'mytournament/vote00.html', {
        "main_nav": main_nav(request.user, 'student_linkback'),
        "bracket": kwargs["bracket"]
    })



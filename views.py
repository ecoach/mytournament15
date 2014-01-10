from django.shortcuts import render_to_response, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.conf import settings
from django.forms.models import inlineformset_factory, modelformset_factory, modelform_factory
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
            bracket.name=row[2]
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
        if new_bracket_form.is_valid():
            name = new_bracket_form.cleaned_data['name']
            print name
            manager = new_bracket_form.cleaned_data['manager']
            print manager
            bracket = Bracket(name=name, manager=manager)
            bracket.save()
            return redirect(reverse('tourney:bracket:manage_bracket', kwargs={'bracket': bracket.id}))
    else:
        new_bracket_form = New_Bracket_Form()
    return render(request, 'mytournament/new_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'new_bracket'),
        'new_bracket_form': new_bracket_form,
    })

@staff_member_required
def choose_bracket_view(request, **kwargs):
    if request.method == 'POST':
        select_bracket_form = Select_Bracket_Form(data=request.POST)
        if select_bracket_form.is_valid():
            bracket = select_bracket_form.cleaned_data['bracket']
            print bracket
            return redirect(reverse('tourney:bracket:manage_bracket', kwargs={'bracket': bracket.id}))
    else:
        select_bracket_form = Select_Bracket_Form()
    return render(request, 'mytournament/choose_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'choose_bracket'),
        'select_bracket_form': select_bracket_form,
    })

@staff_member_required
def manage_bracket_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:choose_bracket'))
    if request.method == 'POST':
        edit_bracket_form = Edit_Bracket_Form(data=request.POST)
        if edit_bracket_form.is_valid():
            status = edit_bracket_form.cleaned_data['status']
            print status
            bracket.status = status
            bracket.save()
    edit_bracket_form = Edit_Bracket_Form(instance=bracket)
    return render(request, 'mytournament/manage_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_bracket', bid=bracket.id),
        "bracket": bracket,
        "registration_link": HttpRequest.build_absolute_uri(request, reverse('tourney:bracket:register', kwargs={'bracket': bracket.id})),
        "voting_link": HttpRequest.build_absolute_uri(request, reverse('tourney:bracket:vote', kwargs={'bracket': bracket.id})),
        'edit_bracket_form': edit_bracket_form,
    })

@staff_member_required
def manage_competitors_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:choose_bracket'))
    CompFormSet = modelformset_factory(
        Competitor,
        can_delete=False,
        form=Competitor_Form,
        extra = 0,
    )
    if request.method == 'POST':
        # formset method
        compformset = CompFormSet(
            prefix='comps',
            data=request.POST, 
        )
        if compformset.is_valid():
            compformset.save()
        # csv method
        form = Competing_Csv_Form(request.POST, request.FILES)
        if form.is_valid():
            cfile = form.cleaned_data['game_file']
            ids = cfile.read().splitlines()
            # create the sample
            for cid in ids:
                print cid
                try:
                    comp = Competitor.objects.get(bracket=bracket, name=cid)
                    comp.Set_Competing()
                except:
                    pass
    competingform = Competing_Csv_Form()
    compformset = CompFormSet(
        prefix='comps',
        queryset=Competitor.objects.filter(bracket=bracket)
    )
    return render(request, 'mytournament/manage_competitors.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_competitors', bid=bracket.id),
        "bracket": bracket,
        "competingform": competingform,
        "compformset": compformset,
    })

@staff_member_required
def manage_judges_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:choose_bracket'))
    if request.method == 'POST':
        importform = Import_Judges_Form(
            data=request.POST, 
        )
        if importform.is_valid():
            trigger = importform.cleaned_data['trigger']
            print trigger
            comps = Competitor.objects.filter(bracket=bracket, status='Competing')
            for cc in comps:
                judge = Judge.objects.get_or_create(bracket=bracket, name=cc.name)[0]
                judge.eligable = 3
                judge.decisions = 0
                judge.save() 
    importform = Import_Judges_Form()
    judges = Judge.objects.filter(bracket=bracket)
    return render(request, 'mytournament/manage_judges.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_judges', bid=bracket.id),
        "bracket": bracket,
        "judges": judges,
        "importform": importform,
    })

@staff_member_required
def review_bracket_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:choose_bracket'))
    comps = Competitor.objects.filter(bracket=bracket, status='Competing')
    return render(request, 'mytournament/review_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'review_bracket', bid=bracket.id),
        "bracket": bracket,
        "comps": comps,
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
        "bracket": bracket.name 
    })

def pdf_register_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
    # load the manager
    manager = eval(bracket.manager)(bracket=bracket)
    
    if request.method == 'POST':
        form = Pdf_Register_Form(request.POST, request.FILES)
        if form.is_valid():
            gfile = form.cleaned_data['game_file']
            # store it...
            gfile_name = 'game.pdf'
            gname = manager.Register(request.user.username, gfile_name)
            if gname != None:
                destination = open(settings.DIR_TOURNEY_PDF + gname, 'wb+')
                for chunk in gfile.chunks():
                    destination.write(chunk)
                destination.close()
    else:
        form = Pdf_Register_Form()

    return render(request, 'mytournament/register.html', {
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket,
        "form": form,
        'competitor': manager.GetCompetitor(request.user)
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
        "bracket": bracket.name,
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
        "bracket": bracket.name,
        "form": form,
        "judge": manager.Get_Judge(request.user.username),
        "status": manager.Status(request.user.username),
        "winner": manager.GetWinner()
    })

def get_bracket(bid):
    # find/create the bracket
    brackets = Bracket.objects.filter(pk=bid)
    if brackets.count() == 0:
        return None
    return brackets[0] 

@staff_member_required
def Download_Mysql_View(request):
    import pdb; pdb.set_trace() 
    import os, time
    # if not admin don't do it
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('/')

    # send the results
    try:
        now = time.strftime('%Y-%m-%d-%H-%M-%S')         
        file_name = settings.DB_NAME + "_" + now + ".sql"
        file_path = settings.DIR_DOWNLOAD_DATA + "mysql/" + file_name
        
        os.system("mysqldump -u ecoach -pecoach " + settings.DB_NAME + " > " + file_path)

        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound("error creating backup database file")

    return response



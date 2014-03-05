from django.shortcuts import render_to_response, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.conf import settings
from django.forms.models import inlineformset_factory, modelformset_factory, modelform_factory
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
def manage_roster_view(request, **kwargs):
    if request.method == 'POST':
        form = Roster_Csv_Form(request.POST, request.FILES)
        if form.is_valid():
            cfile = form.cleaned_data['roster_file']
            ids = cfile.read().splitlines()
            # delete roster
            Roster.objects.all().delete()
            # create new roster
            for cid in ids:
                member = Roster.objects.get_or_create(name=cid.strip())
    form = Roster_Csv_Form()
    roster = Roster.objects.all()
    return render(request, 'mytournament/manage_roster.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'manage_roster'),
        "form": form,
        "roster": roster,
    })

@staff_member_required
def new_bracket_view(request, **kwargs):
    if request.method == 'POST':
        new_bracket_form = New_Bracket_Form(data=request.POST)
        if new_bracket_form.is_valid():
            name = new_bracket_form.cleaned_data['name']
            manager = new_bracket_form.cleaned_data['manager']
            feedback_option = new_bracket_form.cleaned_data['feedback_option']
            bracket = Bracket(name=name, manager=manager, feedback_option=feedback_option)
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
    # load the manager
    manager = eval(bracket.manager)(bracket=bracket)
    if request.method == 'POST':
        edit_bracket_form = Edit_Bracket_Form(data=request.POST)
        if edit_bracket_form.is_valid():
            status = edit_bracket_form.cleaned_data['status']
            bracket.status = status
            name = edit_bracket_form.cleaned_data['name']
            bracket.name = name
            prompt = edit_bracket_form.cleaned_data['prompt']
            bracket.prompt = prompt
            feedback_option = edit_bracket_form.cleaned_data['feedback_option']
            bracket.feedback_option = feedback_option
            bracket.save()
            # take care of auto promotion
            trigger = edit_bracket_form.cleaned_data['trigger']
            if trigger:
                bracket.status='Active'
                bracket.save()
                ids = [rr.name for rr in Roster.objects.all()]
                for cid in ids:
                    try:
                        # promote to competing from roster
                        comp = Competitor.objects.get(bracket=bracket, name=cid)
                        comp.Set_Competing()
                    except:
                        pass
                    # promote to juding from roster
                    judge = Judge.objects.get_or_create(bracket=bracket, name=cid)
                    judge[0].eligable = manager.Default_Eligable()
                    # don't overwrite existing decisions
                    if judge[1]:
                        judge[0].decisions = 0
                    judge[0].save() 
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
def clone_bracket_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:choose_bracket'))
    # load the manager
    original_id = bracket.id
    manager = eval(bracket.manager)(bracket=bracket)
    if request.method == 'POST':
        clone_bracket_form = Clone_Bracket_Form(data=request.POST)
        if clone_bracket_form.is_valid():
            triggers_bracket = clone_bracket_form.cleaned_data['triggers_bracket']
            triggers_competitors = clone_bracket_form.cleaned_data['triggers_competitors']
            triggers_judges = clone_bracket_form.cleaned_data['triggers_judges']
            bracket_instructions = {
                'pk_instructions':{
                },
                'fk_instructions':{
                }
            }
            # bracket
            if triggers_bracket == 'Open':
                bracket_instructions['pk_instructions']['status'] = 'Open'
            elif triggers_bracket == 'Active':
                bracket_instructions['pk_instructions']['status'] = 'Active'
            # competitors
            if triggers_competitors == 'with':
                bracket_instructions['fk_instructions']['competitor'] = {
                    'pk_instructions':{
                        'beat': None,
                        'beatby': None,
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'byes': 0,
                        'points': 0,
                        #'status': 'Competing',
                    },
                    'fk_instructions':{}
                }
            # judges
            if triggers_judges == 'with':
                bracket_instructions['fk_instructions']['judge'] = {
                    'pk_instructions':{
                        'decisions': 0,
                    },
                    'fk_instructions':{}
                }
            new = bracket.clone(bracket_instructions) # clone changes self, new and bracket are same!
            #bracket = Bracket.objects.get(pk=original_id) # restore bracket for debugging
            return redirect(reverse('tourney:bracket:manage_bracket', kwargs={'bracket': new.id}))
    else:
        clone_bracket_form = Clone_Bracket_Form()
    return render(request, 'mytournament/clone_bracket.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'tourney'),
        "steps_nav": steps_nav(request.user, 'clone_bracket', bid=bracket.id),
        "bracket": bracket,
        'clone_bracket_form': clone_bracket_form,
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
    # load the manager
    manager = eval(bracket.manager)(bracket=bracket)
    if request.method == 'POST':
        importform = Import_Judges_Form(
            data=request.POST, 
        )
        if importform.is_valid():
            trigger = importform.cleaned_data['trigger']
            comps = Competitor.objects.filter(bracket=bracket, status='Competing')
            for cc in comps:
                judge = Judge.objects.get_or_create(bracket=bracket, name=cc.name)
                judge[0].eligable = manager.Default_Eligable()
                # don't overwrite existing decisions
                if judge[1]:
                    judge[0].decisions = 0
                judge[0].save() 
    importform = Import_Judges_Form()
    judges = Judge.objects.filter(bracket=bracket).extra(select={'rank': 'eligable - decisions'}).order_by('-rank')
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
    comps = Competitor.objects.filter(bracket=bracket, status='Competing').extra(select={'rank': 'wins - losses'}).order_by('-rank')
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
        "bracket": bracket
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

def competitor_comments_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
    comp = Competitor.objects.get_or_create(id=kwargs['competitor'])
    if comp[1]:
        return redirect(reverse('tourney:default'))
    return render(request, 'mytournament/competitor_comments.html', {
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket,
        'comments': comp[0].Get_Comments()
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
        "bracket": bracket,
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
    # run manager setup
    manager.Setup(request.user.username) 
    # handle the form
    bout = manager.Get_Bout(request.user.username)
    if request.method == 'POST':
        form = Voter_Form(
            data=request.POST,
        )
        if form.is_valid():
            if form.cleaned_data['ballot'] == 'A':
                winner = bout.compA
            else: 
                winner = bout.compB
            feedbackA = form.cleaned_data['feedbackA']
            feedbackB = form.cleaned_data['feedbackB']
            manager.Record_Vote(bout, request.user.username, winner, feedbackA, feedbackB)
            manager.Setup(request.user.username) 
            bout = manager.Get_Bout(request.user.username)
            if bout == None:
                form = Voter_Form(instance=bout)
            else:
                form = Voter_Form(instance=bout, initial={'boutid': bout.id})
    else:
        if bout == None:
            form = Voter_Form(instance=bout)
        else:
            form = Voter_Form(instance=bout, initial={'boutid': bout.id})
    try:
        compA_link = HttpRequest.build_absolute_uri(request, bout.compA.Game_Url())
        compB_link = HttpRequest.build_absolute_uri(request, bout.compB.Game_Url())
        remaining = bout.judge.eligable - bout.judge.decisions
    except:
        compA_link = ''
        compB_link = ''
        remaining = ''
    return render(request, 'mytournament/vote.html', {
        "main_nav": main_nav(request.user, 'student_view'),
        "bracket": bracket,
        "status": manager.Status(request.user.username),
        "competitors": manager.GetWinners(),
        "compA_link": compA_link,
        "compB_link": compB_link,
        "remaining": remaining,
        "form": form,
    })

def get_bracket(bid):
    # find/create the bracket
    brackets = Bracket.objects.filter(pk=bid)
    if brackets.count() == 0:
        return None
    return brackets[0] 

@staff_member_required
def Download_Mysql_View(request):
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

@staff_member_required
def download_ranks_view(request, **kwargs):
    bid = kwargs["bracket"]
    bracket = get_bracket(bid)
    if bracket == None:
        return redirect(reverse('tourney:default'))
    try:        
        # construct ranking for bracket participants
        participants = dict()
        # add competitor stats 
        comps = Competitor.objects.filter(bracket=bracket, status='Competing').extra(select={'rank': 'wins - losses'}).order_by('-rank')
        cut = int(len(comps) / 3.0)
        if len(comps) > cut:
            cut_rank = comps[cut].rank 
        for cc in comps:
            if not cc.name in participants.keys():
                participants[cc.name] = dict()
            participants[cc.name]['game']=cc.game
            participants[cc.name]['wins']=cc.wins
            participants[cc.name]['losses']=cc.losses
            participants[cc.name]['wins_minus_losses']=(cc.wins - cc.losses)
            if cc.rank >= cut_rank:
                participants[cc.name]['rank_credit']=2
            else:
                participants[cc.name]['rank_credit']=1
        # add judge stats
        judges = Judge.objects.filter(bracket=bracket)
        for vv in judges:
            if not vv.name in participants.keys():
                participants[vv.name] = dict()
            participants[vv.name]['eligable']=vv.eligable
            participants[vv.name]['decisions']=vv.decisions
            if vv.eligable == vv.decisions:
                participants[vv.name]['vote_credit']=1
        # total credit calc
        for pp in participants:
            participants[pp]['total_credit'] = participants[pp].get('rank_credit', 0) + participants[pp].get('vote_credit', 0)
        # create the download rows
        lines = ['name,game,wins,losses,wins_minus_losses,rank_credit,eligable,decisions,vote_credit,total_credit']
        for pp in participants:
            lines.append(','.join([
            pp,
            participants[pp].get('game', ''),
            str(participants[pp].get('wins', '')),
            str(participants[pp].get('losses', '')),
            str(participants[pp].get('wins_minus_losses', '')),
            str(participants[pp].get('rank_credit', '')),
            str(participants[pp].get('eligable', '')),
            str(participants[pp].get('decisions', '')),
            str(participants[pp].get('vote_credit', '')),
            str(participants[pp].get('total_credit', '')),
            ]))
        output = "\n".join(lines)
        #response = HttpResponse("one,two \n1,2", content_type='application/octet-stream')
        response = HttpResponse(output, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=ranks.csv'
        return response
    except IOError:
        return redirect(reverse('tourney:bracket:review_bracket ', kwargs={'bracket': bracket.id}))



from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.db.models import F, Q
from datetime import datetime
import json
import numpy as np


# Create your models here.


class Clonable(object):

    def __init__(self):
        pass

    def clone(self, instructions={'pk_instructions':{}, 'fk_instructions':{}}):
        """
        # example dictionary of instructions:
        instructions = {
            pk_instructions: {
                # preserves unspecified attributes
                # overwrites specified attributes
                fieldX: valueX,
                ...
            },
            fk_instructions: {
                # drops unspecified fk objects
                # clones specified fk objects
                fk_key: {pk_instructions, fk_instructions}
                ...
            } 
        }
        """
        # find list of related fk objects
        fk_objs = dict()
        for fk_field in instructions['fk_instructions'].keys():
            fk_objs[fk_field] = eval('self.'+fk_field+'_set.select_related()')
        # create new instance of pk, modify fields and save clone
        self.id = None
        for pk_field in instructions['pk_instructions'].keys():
            if hasattr(self, pk_field):
                setattr(self, pk_field, instructions['pk_instructions'][pk_field])
        self.save() # auto associates the new fk reference for all fk_objs!
        # for any fk objects with clone instructions, recurse
        for fk_set in fk_objs:
            if fk_set in instructions['fk_instructions'].keys():
                for fk_obj in fk_objs[fk_set]: 
                    fk_obj.clone(instructions['fk_instructions'][fk_set])
        return self

COMP_STATUS_CHOICES = (
    ('Registered', 'Registered'),
    ('Competing', 'Competing'),
)

ROSTER_STATUS_CHOICES = (
    ('Enrolled', 'Enrolled'),
)

class Roster(models.Model):
    class Meta: 
        db_table = 'mytournament_roster'
    name = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, default='Enrolled', choices=ROSTER_STATUS_CHOICES)
 

MANAGER_CHOICES = (
    ('Absolute_Order', 'Ordering'),
    ('Single_Elimination', 'Single Winner'),
)

BRACKET_STATE_CHOICES = (
    ('Open', 'Open'),
    ('Active', 'Active'),
    ('Finished', 'Finished'),
)

MANAGER_CHOICES = (
    ('Absolute_Order', 'Ordering'),
    ('Single_Elimination', 'Single Winner'),
)

FEEDBACK_CHOICES = (
    ('Required', 'Required'),
    ('Optional', 'Optional'),
)

class Bracket(models.Model, Clonable):
    class Meta: 
        db_table = 'mytournament_bracket'
    # [12m_Competitor]
    # [12m_Judge]
    # [12m_Bout]
    name = models.CharField(max_length=100)
    prompt = models.TextField(null=True, blank=True)
    feedback_option = models.CharField(default='Optional', max_length=30, choices=FEEDBACK_CHOICES)
    manager = models.CharField(max_length=30, choices=MANAGER_CHOICES)
    status = models.CharField(default='Open', max_length=30, choices=BRACKET_STATE_CHOICES)

    def __unicode__(self):
        return str(self.id) + '_' + self.name

    def percent_complete(self):
        judges = Judge.objects.filter(bracket=self).extra(select={'rank': 'eligable - decisions'}).order_by('-rank')
        try:
            return int(np.mean([float(vv.decisions)/float(vv.eligable) for vv in judges])*100)
        except:
            return 0

    def num_judges(self):
        return len(Judge.objects.filter(bracket=self))


class Competitor(models.Model, Clonable):
    class Meta: 
        db_table = 'mytournament_competitor'
    # [12m_Bout]
    bracket = models.ForeignKey(Bracket)
    name = models.CharField(max_length=30, null=True, blank=True)
    game = models.TextField(null=True, blank=True)
    beat = models.TextField(null=True, blank=True)      # json array of who they beat
    beatby = models.TextField(null=True, blank=True)    # json array of who beat them
    wins = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)
    draws = models.IntegerField(null=True, blank=True)
    byes = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, default='Registered', choices=COMP_STATUS_CHOICES)

    def Set_Competing(self):
        self.status = 'Competing'
        self.save()

    def Game_Url(self):
        import time
        tt = str(time.time())
        return reverse('tourney:tourney_pdf', kwargs={'path': self.game}) + "?"+tt

    def Feedback_Url(self):
        return reverse('tourney:bracket:competitor_feedback', kwargs={'competitor': self.id, 'bracket':self.bracket.id})

    def Get_Comments(self):
        comments = []
        for bb in self.compA.select_related():
            if bb.feedbackA != None and len(bb.feedbackA) > 0:
                comments.append(bb.feedbackA)
        for bb in self.compB.select_related():
            if bb.feedbackB != None and len(bb.feedbackB) > 0:
                comments.append(bb.feedbackB)
        return comments

    def Get_Beatby(self):
        try: 
            ret = json.loads(self.beatby)
            if isinstance(ret, list):
                return ret
        except:
            pass
        return []

    def Get_Beat(self):
        try: 
            ret = json.loads(self.beat)
            if isinstance(ret, list):
                return ret
        except:
            pass
        return []

    def Set_Beatby(self, beatby):
        self.beatby = json.dumps(beatby)
        self.save()
   
    def Set_Beat(self, beat):
        self.beat = json.dumps(beat)
        self.save()

    def Add_Beat(self, who):
        beat = self.Get_Beat() 
        beat.append(who)
        self.Set_Beat(beat)
     
    def Add_Beatby(self, who):
        beatby = self.Get_Beatby() 
        beatby.append(who)
        self.Set_Beatby(beatby)
    
class Judge(models.Model, Clonable):
    class Meta: 
        db_table = 'mytournament_judge'
    # [12m_Bout]
    bracket = models.ForeignKey(Bracket)
    name = models.CharField(max_length=30, null=True, blank=True)
    eligable = models.IntegerField(default=0)
    decisions = models.IntegerField(default=0)
    skips = models.IntegerField(default=0)
    rating = models.IntegerField(null=True, blank=True)

class Bout(models.Model, Clonable):
    class Meta: 
        db_table = 'mytournament_bout'
    bracket = models.ForeignKey(Bracket)
    bround = models.IntegerField(null=True, blank=True)
    judge = models.ForeignKey(Judge, null=True)
    compA = models.ForeignKey(Competitor, related_name='compA')
    compB = models.ForeignKey(Competitor, related_name='compB')
    feedbackA = models.TextField(null=True, blank=True)
    feedbackB = models.TextField(null=True, blank=True)
    winner = models.ForeignKey(Competitor, related_name='winner', null=True)
    btime = models.DateTimeField(null=True, blank=True)


class Base_Tourney(object):

    def __init__(self, bracket):
        self.bracket = bracket

    def Register(self, name, game):
        #if not self.bracket.ready:
        if self.bracket.status == 'Open':
            cc = Competitor.objects.get_or_create(bracket=self.bracket, name=name)[0]
            cc.wins = 0
            cc.losses = 0
            cc.points = 0
            cc.byes = 0
            cc.status = 'Registered'
            cc.save()
            cc.game = '_'.join([str(cc.id), game]) # make sure game is unique...
            cc.save()
            return cc.game
        return None

    def GetCompetitor(self, user):
        try:
            return Competitor.objects.get(bracket=self.bracket, name=user.username)
        except:
            return ""

    def Game(self, user):
        try:  
            return Competitor.objects.get(bracket=self.bracket, name=user.username).game
        except:
            return ""

    def Setup(self, who):
        # cascade events
        self.Round_Cleanup() 
        #if self.bracket.finished:
        if self.bracket.status == 'Finished':
            return
        judge = self.Get_Judge(who)
        if self.Round_Complete(judge):
            self.Advancing()
            self.RePair()

    def Votes_Remaining_Judge(self, who):
        return self.bracket.judge_set.filter(eligable__gt=F('decisions'), name=who)

    def Decisions_Remaining_Bracket(self):
        return self.bracket.judge_set.filter(eligable__gt=F('decisions'))
        #judgements = judgements.filter(~Q(name=who))
    
    def Get_Judge(self, who):
        # get judge object for voter
        try:
            judge = Judge.objects.get(bracket=self.bracket, name=who)
            return judge
        except:
            return False

    def Round_Cleanup(self):
        # if judges havent' been loaded yet don't clean up and set to finished
        if len(self.bracket.judge_set.all()) == 0:
            return          
        # if there aren't any judgements left we're done (plus clean up party trash)
        #if len(self.Decisions_Remaining_Bracket()) == 0  or self.bracket.finished == 1:
        if len(self.Decisions_Remaining_Bracket()) == 0  or self.bracket.status == 'Finished':
            # bracket can finish for other reasons...in which case cleanup can still happen
            #self.bracket.finished = 1
            self.bracket.status = 'Finished'
            self.bracket.save()
            # find all the dangling bouts (party trash) and delete them
            Bout.objects.filter(bracket=self.bracket, winner__isnull=True).delete()
            return 

        # remove dangling vote assignments
        # look up all active vote assignments for this bracket
        # spin over and clear any that are older than 15 minutes
        dangling = Bout.objects.filter(bracket=self.bracket, winner__isnull=True, btime__isnull=False)
        for bb in dangling:
            tnow = datetime.utcnow()
            tthen = bb.btime
            del_minutes = (tnow.replace(tzinfo=None) - tthen.replace(tzinfo=None)).seconds / 60
            if del_minutes >= 20:
                bb.judge = None
                bb.btime = None
                bb.save()

    def Round_Complete(self, judge):
        # check if there are any bouts remaining in current/last round
        all_rounds = self.bracket.bout_set.all()
        if len(all_rounds) == 0:
            return True
        last_round = all_rounds.aggregate(Max('bround'))
        current_round = last_round['bround__max']
        remain = all_rounds.filter(bround=current_round, winner__isnull=True)
        #remain = all_rounds.filter(~Q(judge=judge), bround=current_round, winner__isnull=True)
        return (len(remain) == 0)

    def Default_Eligable(self):
        return 1

    def RePair(self):
        pass

    def Advancing(self):
        # only winners advance in single elimination
        pass 

    def Get_Next_Round_Number(self):
        # assumes last round is complete 
        all_rounds = self.bracket.bout_set.all()
        # no bouts yet means first round
        if len(all_rounds) == 0:
            return 1
        last_round = all_rounds.aggregate(Max('bround'))
        return (last_round['bround__max'] + 1)

    def Status(self, who):
        #if self.bracket.finished: # everyone can see once it's done
        if self.bracket.status == 'Finished': # everyone can see once it's done
            return "MESSAGE_WINNER" 
        if not self.Status_Participating(who):
            return "MESSAGE_NON_PART"
        elif self.Status_Wait(who):
            return "MESSAGE_WAIT"
        elif self.Status_Vote_Ready(who):
            return "MESSAGE_VOTE"
        elif self.Status_Vote_Done(who): 
            return "MESSAGE_THANKS"
        else:
            return "MESSAGE_WINNER"

    def GetWinners(self):
        # this should maybe print the ordering results...
        comps = self.bracket.competitor_set.filter(status='Competing').extra(select={'rank': 'wins - losses'}).order_by('-rank')
        winners = []
        for cc in comps:
            #cc.compB.select_related()[3].feedbackA
            game_link = "<a href='" + cc.Game_Url() +"' onclick=\"logger.page_dynamics('winners_pdf', '"+cc.game+"');\" target='_blank'>" + cc.game + "</a>"
            comments = cc.Get_Comments()
            if len(comments) > 0:
                feedback_link = "<a href='" + cc.Feedback_Url() +"'>comments: "+str(len(comments))+"</a>"
            else:
                feedback_link = ''
            winners.append([cc.wins, cc.losses, game_link, feedback_link]) 
        return winners

    def Status_Participating(self, who):
        # check if you're assigned to vote in this bracket
        judge = self.Get_Judge(who)
        if not judge:
            return False
        return True 

    def Status_Wait(self, who):
        # check if the voting assignments are all distributed for this round 
        # should already know they are a judge (they would have got non-part msg)
        # this depends on cleanup running first...
        #if self.bracket.finished == 1:
        if self.bracket.status == 'Finished':
            return False
        if self.Decisions_Remaining_Bracket() == 0:
            return False
        if len(self.Votes_Remaining_Judge(who)) == 0:
            return False
        if not self.Bout_Assignment(who): # this being third requires above both false
            return True
        return False

    def Status_Vote_Ready(self, who):
        # make sure they have a bout assigned and there's not already a winner
        return self.Bout_Assignment(who)

    def Status_Vote_Done(self, who):
        #if self.bracket.finished:
        if self.bracket.status == 'Finished':
            return False
        return True
        pass

    def Get_Bout(self, who):
        bout = self.Bout_Assignment(who)
        if not bout:
            return None
        return bout

    def Vote_Choices(self, who):
        import time
        tt = str(time.time())
        bout = self.Bout_Assignment(who)
        if not bout:
            return [('some_url', "<a href=''>if you get see this please report it...</a>"), 
                    ('another_url',"<a href=''>for some reason bout not ready for this bracket!</a>")] 
        return [(bout.compA.game, "<a href='" + reverse('tourney:tourney_pdf', kwargs={'path': bout.compA.game}) + "?"+tt+"' class='data-log-external' target='_blank'>submission 1 (click to review " + bout.compA.game + ")</a>"), 
                    (bout.compB.game,"<a href='" + reverse('tourney:tourney_pdf', kwargs={'path': bout.compB.game}) + "?"+tt+"' class='data-log-external' target='_blank'>submission 2 (click to review " + bout.compB.game + ")</a>")] 

    def Vote_Choices_Old(self, who):
        bout = self.Bout_Assignment(who)
        if not bout:
            return [('some_url', "<a href='" + 'some_url' + "'>if you get see this please report it...</a>"), 
                    ('another_url',"<a href='" + 'another_url' + "'>for some reason bout not ready for this bracket!</a>")] 
        return [(bout.compA.game, "<a href='" + bout.compA.game + "' class='data-log-external' target='_blank'>submission 1 (click to review " + bout.compA.game + ")</a>"), 
                    (bout.compB.game,"<a href='" + bout.compB.game + "' class='data-log-external' target='_blank'>submission 2 (click to review " + bout.compB.game + ")</a>")] 

       
    def Bout_Assignment(self, who):
        # make sure they have votes left
        dec = self.Votes_Remaining_Judge(who)
        if len(dec) == 0:
            return False
        judge = dec[0] 
        # check if bout assignment already exists
        on_deck = self.bracket.bout_set.filter(judge=judge, winner__isnull=True)
        if len(on_deck) > 0:
            return on_deck[0]
        # or try to make a new bout assignment 
        in_hole = self.bracket.bout_set.filter(judge__isnull=True, winner__isnull=True)
        for bout in in_hole:
            # don't assign someone their own stuff to judge!
            if bout.compA.name != who and bout.compB.name != who:
                bout.judge = judge
                bout.btime = datetime.now()
                bout.save()
                return bout
        return False

    def Bout_Id(self, who):
        bout = self.Bout_Assignment(who)
        if not bout:
            return 0
        return bout.id

    def Record_Vote(self, bout, judgename, winner, feedbackA, feedbackB):
        judge = bout.judge
        if judge.name != judgename:
            # must have timed out!
            return
        if winner == bout.compA:
            looser = bout.compB
        else:
            looser = bout.compA
        # set record the competitors stats
        judge.decisions += 1
        judge.save()
        looser.losses += 1
        looser.Add_Beatby(winner.name)
        looser.save()
        winner.wins += 1 
        winner.Add_Beat(looser.name)
        winner.save()
        # record the bout winner and feedback
        bout.winner = winner
        bout.feedbackA = feedbackA
        bout.feedbackB = feedbackB
        bout.save()

class Single_Elimination(Base_Tourney):

    def __init__(self, **kwargs):
        super(Single_Elimination, self).__init__(**kwargs)

    def RePair(self):
        bround = self.Get_Next_Round_Number()
        comp_res = Competitor.objects.filter(bracket=self.bracket, losses=0, status='Competing').extra(order_by = ['byes'])
        competitors = [x for x in comp_res]
        # check if a winner has already been found...
        if len(competitors) == 1:
            # this only needs to happen once...competitors may loose in negative rounds...no matter
            winner = competitors[0]
            winner.save()
            # check if judgements remain and retrace or declare a winner
            judgements = self.Decisions_Remaining_Bracket()
            # works in single elimination 
            # this creates party trash when the last person to vote submits...extra bout
            repeats = Bout.objects.filter(winner=winner, judge__isnull=False).order_by('btime')
            for ii in range(0, len(judgements)):
                bout = Bout(bracket=self.bracket, bround=-repeats[ii].bround, judge=None, compA=repeats[ii].compA, compB=repeats[ii].compB)
                bout.save() 
            return
        # handle the bye
        if len(competitors) % 2 > 0:
            bye = competitors[0]
            competitors = competitors[1:]
            btime = datetime.now()
            bout = Bout(bracket=self.bracket, bround=bround, judge=None, compA=bye, compB=bye, winner=bye, btime=btime)
            bout.save()
            bye.byes += 1
            bye.wins += 1
            bye.save()
        comps = []
        while(len(competitors) > 1):
            one = competitors.pop()
            two = competitors.pop()
            comps.append([one,two])
        for cc in comps:
            bout = Bout(bracket=self.bracket, bround=bround, judge=None, compA=cc[0], compB=cc[1])
            bout.save() 

class Absolute_Order(Base_Tourney):

    def __init__(self, **kwargs):
        super(Absolute_Order, self).__init__(**kwargs)

    def Advancing(self):
        # everyone advances
        pass

    def Default_Eligable(self):
        return 3

    def RePair(self):
        if len(self.Decisions_Remaining_Bracket()) == 0:
            return
        bround = self.Get_Next_Round_Number()
        comp_res = Competitor.objects.filter(bracket=self.bracket, status='Competing')
        competitors = [x for x in comp_res]
        # make groups of competitors
        comp_groups = dict()
        win_set_size = len(set([x.wins for x in self.bracket.competitor_set.filter(status='Competing')]))
        comp_set_size = len(self.bracket.competitor_set.filter(status='Competing'))
        match_losses = False
        if win_set_size == comp_set_size:
            match_losses = True
        for cc in competitors:
            gparam = cc.wins
            if match_losses:
                gparam = cc.losses
            #gparam = cc.wins - cc.losses
            #gparam = round(float(cc.losses) / (cc.wins + 1), 1)
            if not gparam in comp_groups.keys():
                comp_groups[gparam] = []
            comp_groups[gparam].append(cc)
        cgroups = []
        keys = sorted(comp_groups.keys(), reverse=True)
        for gg in keys:
            cgroups.append(comp_groups[gg])
        useful=0
        for gg in cgroups:  
            useful += self.CreateRound(gg, bround)
        # when no bouts are found at all things are done
        if useful == 0:
            #self.bracket.finished = 1
            self.bracket.status = 'Finished'
            self.bracket.save()
 
    def CreateRound(self, comps, rnd):
        from random import shuffle
        bouts = [] # list of bouts in that round
        comps.sort(key=lambda x: (x.wins - x.losses), reverse=True) 
        if rnd == 1: # first round is randomized (helps with clone experiment)
            shuffle(comps)
        byes_tally = []
        #decisions_remaining = sum([x.eligable - x.decisions for x in self.Decisions_Remaining_Bracket()])
        # this does fold the sorted list :)
        while(len(comps) > 0):
        #while(len(comps) > 0 and decisions_remaining > 0):
            one = comps.pop()
            one.byes += 1
            one.save()
            byes_tally.append(one)
            for two in comps:
                two.Get_Beat()
                if not one.name in (two.Get_Beat() + two.Get_Beatby()):
                    one.byes -= 1
                    one.save()
                    byes_tally.pop()
                    bouts.append([one,two]) 
                    comps.remove(two)
                    #decisions_remaining -= 1
                    break
        if len(bouts) < 1:
            return 0
        for cc in bouts:
            bout = Bout(bracket=self.bracket, bround=rnd, judge=None, compA=cc[0], compB=cc[1])
            bout.save()
        return 1
 
class Top(Base_Tourney):
    seeking = 3

    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)

    def Advancing(self):
        # decide if selection or elimination round
        # find everyone who is advancing to the next round
        # set status of those selected/eliminated
        pass 


class Top20(Top):
    seeking = 3

    def __init__(self, **kwargs):
        super(Top20, self).__init__(**kwargs)

class Top10(Top):
    seeking = 10

    def __init__(self, **kwargs):
        pass

class Genetic(Base_Tourney):

    def __init__(self, **kwargs):
        pass

class Swiss_Style(Base_Tourney):

    def __init__(self, **kwargs):
        pass





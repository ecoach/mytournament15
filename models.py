from django.db import models

# Create your models here.

class Bracket(models.Model):
    # [12m_Competitor]
    # [12m_Judge]
    # [12m_Bout]
    name = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    manager = models.CharField(max_length=30, null=True, blank=True)
    ready = models.NullBooleanField()
    finished = models.NullBooleanField()

    def get_bout(self, judge):
        pass
        # check if judge is eligable to make decisions
        # return choices 
        # use manager to decide next set of bouts
        # eval(self.manager).repair()

class Competitor(models.Model):
    # [12m_Bout]
    bracket = models.ForeignKey(Bracket)
    name = models.CharField(max_length=30, null=True, blank=True)
    game = models.TextField(null=True, blank=True)
    wins = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    byes = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

class Judge(models.Model):
    # [12m_Bout]
    bracket = models.ForeignKey(Bracket)
    name = models.CharField(max_length=30, null=True, blank=True)
    eligable = models.IntegerField(null=True, blank=True)
    decisions = models.IntegerField(null=True, blank=True)

class Bout(models.Model):
    bracket = models.ForeignKey(Bracket)
    bround = models.IntegerField(null=True, blank=True)
    judge = models.ForeignKey(Judge, null=True)
    compA = models.ForeignKey(Competitor, related_name='compA')
    compB = models.ForeignKey(Competitor, related_name='compB')
    winner = models.ForeignKey(Competitor, related_name='winner', null=True)
    btime = models.DateTimeField(null=True, blank=True)


class Base_Tourney(object):

    def __init__(self, bracket):
        self.bracket = bracket

    def Register(self, name, game):
        if not self.bracket.ready:
            cc = Competitor.objects.get_or_create(bracket=self.bracket, name=name)[0]
            cc.game = game
            cc.save()

    def Game(self, competitor):
        try:  
            return Competitor.objects.get(bracket=self.bracket, name=competitor.username).game
        except:
            return ""

    def Setup(self, who):
        # cascade events
        self.Round_Cleanup() 
        if self.Round_Complete():
            self.Advancing()
            self.RePair()

    def Round_Cleanup(self):
        # remove dangling vote assignments
        # look up all active vote assignments for this bracket
        # spin over and clear any that are older than 15 minutes
        pass

    def Round_Complete(self):
        # check if there are any bouts remaining in current/last round
        return True
        pass

    def RePair(self):
        pass

    def Advancing(self):
        # only winners advance in single elimination
        pass 

    def Get_Next_Round_Number(self):
        # assumes last round is complete 
        from django.db.models import Max
        all_rounds = self.bracket.bout_set.all()
        # no bouts yet means first round
        if len(all_rounds) == 0:
            return 1
        last_round = all_rounds.aggregate(Max('bround'))
        return (last_round['bround__max'] + 1)

    def Status(self, who):
        if not self.Status_Participating(who):
            return "MESSAGE_NON_PART"
        elif self.Status_Wait(who) == None:
            return "MESSAGE_WAIT"
        elif self.Status_Vote_Ready(who):
            return "MESSAGE_VOTE"
        elif self.Status_Vote_Done(who): 
            return "MESSAGE_THANKS"
        else:
            return "MESSAGE_WINNER"

    def Status_Participating(self, who):
        # check if you're assigned to vote in this bracket
        pass

    def Status_Wait(self, who):
        pass

    def Status_Vote_Ready(self, who):
        pass

    def Status_Vote_Done(self, who):
        pass

    def Vote_Choices(self, judge):
        bout = self.Bout_Assignment(judge)
        return [('some_url', "<a href='" + 'some_url' + "'>problem 1 (click to view problem)</a>"), ('another_url',"<a href='" + 'another_url' + "'>problem 2 (click to view problem)</a>")] 
        # look up the URLs for the judge
        #bouts = Bout.objects.filter(judge=judge).values_list('compA', 'compB')
        #c1 = W_13Data.objects.filter(user_id=bouts[0][0]).values_list('Exam_2_Video_URL')
        #c2 = W_13Data.objects.filter(user_id=bouts[0][1]).values_list('Exam_2_Video_URL')
        #return [(c1[0][0], "<a href='" + c1[0][0] + "'>video 1 (click to watch)</a>"), (c2[0][0],"<a href='" + c2[0][0] + "'>video 2 (click to watch)</a>")] 
        
    def Bout_Assignment(self, judge):
        # if there's not already a vote assignment make a new vote assignment
        # get bout for judge
        #Bout.objects.get(id=0)
        return 0

    def Bout_Id(self, judge):
        try:
            return Bout_Assignment(judge)
        except:
            return 0

    def Record_Vote(self, bout, judge, decision):
        import pdb; pdb.set_trace() 
        # make sure the vote is still assigned to them, may have timed out!
        # record the vote on bout
        # set status of competitors selected/eliminated
        # cascade events
        pass


class Single_Elimination(Base_Tourney):

    def __init__(self, **kwargs):
        super(Single_Elimination, self).__init__(**kwargs)
        pass

    def RePair(self):
        from datetime import datetime
        competitors = Competitor.objects.filter(bracket=self.bracket, losses=0).extra(order_by = ['byes'])
        bround = self.Get_Next_Round_Number()
        # handle the bye
        if len(competitors) % 2 > 0:
            bye = competitors[0]
            competitors = competitors[1:]
            btime = datetime.now()
            bout = Bout(bracket=self.bracket, bround=bround, judge=None, compA=bye, compB=bye, winner=bye, btime=btime)
            bout.save()
            bye.byes += 1
            bye.save()
        comps = []
        while(len(competitors) > 1):
            one = competitors.pop()
            two = competitors.pop()
            comps.append([one,two])
        for cc in comps:
            bout = Bout(bracket=self.bracket, bround=bround, judge=None, compA=cc[0], compB=cc[1])
            bout.save() 

class Top(Base_Tourney):
    seeking = 3

    def __init__(self, **kwargs):
        super(Top, self).__init__(**kwargs)

class Top20(Top):
    seeking = 3

    def __init__(self, **kwargs):
        super(Top20, self).__init__(**kwargs)

class Top10(Top):
    seeking = 10

    def __init__(self):
        pass

class Genetic(Base_Tourney):

    def __init__(self):
        pass

class Absolute_Order(Base_Tourney):

    def __init__(self):
        pass

    def Advancing(self):
        # decide if selection or elimination round
        # find everyone who is advancing to the next round
        # set status of those selected/eliminated
        pass 

class Swiss_Style(Base_Tourney):

    def __init__(self):
        pass





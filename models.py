from .managers import *
from django.db import models

# Create your models here.

class Bracket(models.Model):
    # [12m_Competitor]
    # [12m_Judge]
    # [12m_Bout]
    name = models.CharField(max_length=30, null=True, blank=True)
    manager = models.CharField(max_length=30, null=True, blank=True)
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
    rnd = models.IntegerField(null=True, blank=True)
    compA = models.ForeignKey(Competitor, related_name='compA')
    compB = models.ForeignKey(Competitor, related_name='compB')
    judge = models.ForeignKey(Judge, null=True)
    btime = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(Competitor, related_name='winner', null=True)



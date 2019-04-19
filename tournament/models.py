from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms

# Create your models here.
class Tournament(models.Model):
    """ Contains data about the overall tournament.
        Associates the tournament with an owner, which is a user model
    """
    TOURNAMENT_CHOICES = (
        ('SE', 'Single Elimination'),
        ('DE', 'Double Elimination'),
        ('RR', 'Round-Robin'),
        ('SW', 'Swiss')
    )
    # INITIAL_MATCHING_CHOICES = (
    #     ('R', 'Random'),
    #     ('M', 'Manual'),
    #     ('S', 'Seeded'),
    # )
    # tournamentInitialMatching = models.CharField(
    #     max_length=1,
    #     choices=INITIAL_MATCHING_CHOICES,
    #     default='R',
    #     verbose_name='Initial Matching Type',
    # )
    # some sort of owner
    tournamentName = models.CharField(max_length=200, verbose_name='Tournament Name')
    publishDate = models.DateTimeField(verbose_name='Date Published', auto_now_add=True)
    lastUpdatedDate = models.DateTimeField(verbose_name='Last Updated', auto_now=True)
    tournamentType = models.CharField(
        max_length=2,
        choices=TOURNAMENT_CHOICES,
        default='SE',
        verbose_name='Tournament Type'
    )
    numberOfEntrants = models.IntegerField(default=2)
    currentRound = models.IntegerField(default=0)
    owner = models.ForeignKey(User, verbose_name="Owner", on_delete=models.CASCADE)

    def __str__(self):
        return self.tournamentName

class Entrant(models.Model):
    """ Contains information about an entrant in a tournament.
        Associates the Entrant with a specific tournament
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name='Name') #unique=True
    wins = models.IntegerField(default=0, verbose_name='Wins')
    losses = models.IntegerField(default=0, verbose_name='Losses')
    draws = models.IntegerField(default=0, verbose_name='Draws')
    #seed = models.IntegerField(default=0, verbose_name='Seed')
    #team = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    # not used
    def natural_key(self):
        return (self.id, self.name, self.wins, self.losses, self.draws)
    
class Match(models.Model):
    """ Contains information about a single match within a tournament
        Associates the Match with a specific tournament
        Associates with two Entrants, who make the matchup
        Associates with a parent match in SE and DE
    """
    NOWIN = 0
    FIRSTWIN = 1
    SECONDWIN = 2
    DRAW = 3
    BYE = 4
    WINNER_CHOICES = (
        (NOWIN, 'No Winner'),
        (FIRSTWIN, 'First Entrant Winner'),
        (SECONDWIN, 'Second Entrant Winner'),
        (DRAW, 'Draw'),
        (BYE, 'Bye'),
    )
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    firstEntrant = models.ForeignKey(Entrant, default=None, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    secondEntrant = models.ForeignKey(Entrant, default=None, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    depth = models.IntegerField(default=0)
    #matchComplete = models.BooleanField(default=False)
    winner = models.IntegerField(
        default=0,
        choices=WINNER_CHOICES,
        verbose_name="Winner"
    )
    parentMatch = models.ForeignKey('self', default=None, blank=True, null=True, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return str(self.id)

class TournamentForm(ModelForm):
    """ Form for Tournaments, gets the name and type
    """
    class Meta:
        model = Tournament
        fields = ['tournamentName', 'tournamentType']

class EntrantForm(ModelForm):
    """ Form for Entrants, gets the name
    """
    class Meta:
        model = Entrant
        fields = ['name']
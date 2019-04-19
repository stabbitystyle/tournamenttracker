from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.forms import formset_factory
from .models import Tournament, Entrant, Match, TournamentForm, EntrantForm
from .utils import indexContext, createMatches, outputCSV
from django.core import serializers
from django.db.models import Q
from math import ceil

# Create your views here.
def index(request):
    # The render() function takes the request object as its first argument,
    # a template name as its second argument and a dictionary as its optional third argument.
    # It returns an HttpResponse object of the given template rendered with the given context.
    # The negative sign in front of "-lastUpdatedDate" indicates descending order. Ascending order is implied.
    return render(request, 'tournament/index.html', indexContext(request))
    #return HttpResponse("View all your tournaments here.")

def add(request):
    """ View for adding a new tournament.  Uses a formset for entrants and tournamentform for the tournament
        Calls createMatches at the end to generate all the matches for the tournament
    """
    EntrantFormset = formset_factory(EntrantForm)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TournamentForm(request.POST)
        entrantFormset = EntrantFormset(request.POST)
        # check whether it's valid:
        if form.is_valid() and entrantFormset.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            
            tempForm = form.save(commit=False)
            tempForm.owner = request.user
            tempForm.numberOfEntrants = len(entrantFormset)
            tempForm.save()
            tournament = Tournament.objects.get(id=tempForm.id)
            
            entrantList = []
            for entrantForm in entrantFormset:
                name = entrantForm.cleaned_data.get('name')
                if name:
                    entrantList.append(Entrant(name=name, tournament=tournament))
            for entrant in entrantList:
                entrant.save()
            #Entrant.objects.bulk_create(entrantList)
            createMatches(tournament)
            messages.success(request, 'Account created successfully')
            #return render(request, 'tournament/index.html', indexContext(request))
            return redirect('/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = TournamentForm()
        entrantFormset = EntrantFormset()
    context = {'form': form, 'entrantFormset': entrantFormset}
    return render(request, 'tournament/add.html', context)

def display(request, tournament_id):
    """ Displays any of the tournament types
    """
    tournament = get_object_or_404(Tournament, id=tournament_id)
    #handling a POST
    if request.method == 'POST' and tournament.owner.id == request.user.id:
        # handling POST for Single Elimination tournament
        if tournament.tournamentType == 'SE':
            for key, value in request.POST.items():
                print(key, value)
                if value != 0 and key != 'csrfmiddlewaretoken':
                    updatedMatch = get_object_or_404(Match, id=int(key))
                    updatedMatch.winner = int(value[0])
                    updatedMatch.save()
                    if updatedMatch.parentMatch:
                        parent = get_object_or_404(Match, id=updatedMatch.parentMatch.id)
                        if not parent.firstEntrant:
                            if updatedMatch.winner == 1:
                                parent.firstEntrant = updatedMatch.firstEntrant
                            elif updatedMatch.winner == 2:
                                parent.firstEntrant = updatedMatch.secondEntrant
                        else:
                            if updatedMatch.winner == 1:
                                parent.secondEntrant = updatedMatch.firstEntrant
                            elif updatedMatch.winner == 2:
                                parent.secondEntrant = updatedMatch.secondEntrant
                        parent.save()
                    # if it's not a Bye
                    if updatedMatch.firstEntrant and updatedMatch.secondEntrant:
                        # firstEntrant update
                        firstEntrant = get_object_or_404(Entrant, id=updatedMatch.firstEntrant.id)
                        if int(value[0]) == 1:
                            firstEntrant.wins += 1
                        elif int(value[0]) == 2:
                            firstEntrant.losses += 1
                        elif int(value[0]) == 3:
                            firstEntrant.draws += 1
                        firstEntrant.save()
                        # secondEntrant update
                        secondEntrant = get_object_or_404(Entrant, id=updatedMatch.secondEntrant.id)
                        if int(value[0]) == 1:
                            secondEntrant.losses += 1
                        elif int(value[0]) == 2:
                            secondEntrant.wins += 1
                        elif int(value[0]) == 3:
                            secondEntrant.draws += 1
                        secondEntrant.save()
        elif tournament.tournamentType == 'DE':
            print('posted DE')
        # handling POST for Round-Robin tournament
        elif tournament.tournamentType == 'RR':
            print(request.POST)
            for key, value in request.POST.items():
                print(key, value)
                if value != 0 and key != 'csrfmiddlewaretoken':
                    updatedMatch = get_object_or_404(Match, id=int(key))
                    #print(updatedMatch, value)
                    updatedMatch.winner = int(value[0])
                    #updatedMatch.matchComplete = True
                    updatedMatch.save()
                    # if it's not a Bye
                    if updatedMatch.firstEntrant and updatedMatch.secondEntrant:
                        # firstEntrant update
                        updateEntrant = get_object_or_404(Entrant, id=updatedMatch.firstEntrant.id)
                        if int(value[0]) == 1:
                            updateEntrant.wins += 1
                        elif int(value[0]) == 2:
                            updateEntrant.losses += 1
                        elif int(value[0]) == 3:
                            updateEntrant.draws += 1
                        updateEntrant.save()
                        # secondEntrant update
                        updateEntrant = get_object_or_404(Entrant, id=updatedMatch.secondEntrant.id)
                        if int(value[0]) == 1:
                            updateEntrant.losses += 1
                        elif int(value[0]) == 2:
                            updateEntrant.wins += 1
                        elif int(value[0]) == 3:
                            updateEntrant.draws += 1
                        updateEntrant.save()
        elif tournament.tournamentType == 'SW':
            print(request.POST)
            for key, value in request.POST.items():
                print(key, value)
                if value != 0 and key != 'csrfmiddlewaretoken':
                    updatedMatch = get_object_or_404(Match, id=int(key))
                    #print(updatedMatch, value)
                    updatedMatch.winner = int(value[0])
                    #updatedMatch.matchComplete = True
                    updatedMatch.save()
                    # if it's not a Bye
                    if updatedMatch.firstEntrant is not None and updatedMatch.secondEntrant is not None:
                        # firstEntrant update
                        updateEntrant = get_object_or_404(Entrant, id=updatedMatch.firstEntrant.id)
                        if int(value[0]) == 1:
                            updateEntrant.wins += 1
                        elif int(value[0]) == 2:
                            updateEntrant.losses += 1
                        elif int(value[0]) == 3:
                            updateEntrant.draws += 1
                        updateEntrant.save()
                        # secondEntrant update
                        updateEntrant = get_object_or_404(Entrant, id=updatedMatch.secondEntrant.id)
                        if int(value[0]) == 1:
                            updateEntrant.loses += 1
                        elif int(value[0]) == 2:
                            updateEntrant.wins += 1
                        elif int(value[0]) == 3:
                            updateEntrant.draws += 1
                        updateEntrant.save()
            # gets all matches from current round that have a result
            currentMatches = list(Match.objects.filter(tournament=tournament, depth=tournament.currentRound))
            currentMatches = [match for match in currentMatches if match.winner > 0]
            # if the matches 
            if len(currentMatches) == ceil(tournament.numberOfEntrants / 2):
                print(currentMatches)
            #if Match.objects.filter(Q(depth=tournament.currentRound) & ~Q(winner=0)).count() == ceil(tournament.numberOfEntrants / 2):
                tournament.currentRound += 1
                tournament.save()
                createMatches(tournament)
    
    # render block, not much to say
    if tournament.tournamentType == 'SE':
        matches = Match.objects.filter(tournament=tournament).order_by('depth')
        entrants = Entrant.objects.filter(tournament=tournament).order_by('-wins')
        matchCSV = outputCSV(tournament)
        context = {'tournament': tournament, 'matches': matches, 'entrants': entrants, 'matchCSV': matchCSV}
        return render(request, 'tournament/singleelimination.html', context)
    elif tournament.tournamentType == 'DE':
        matches = Match.objects.filter(tournament=tournament)
        entrants = Entrant.objects.filter(tournament=tournament)
        context = {'tournament': tournament, 'matches': matches, 'entrants': entrants}
        return render(request, 'tournament/doubleelimination.html', context)
    elif tournament.tournamentType == 'RR':
        matches = Match.objects.filter(tournament=tournament).order_by('depth')
        entrants = Entrant.objects.filter(tournament=tournament).order_by('-wins')
        context = {'tournament': tournament, 'matches': matches, 'entrants': entrants}
        return render(request, 'tournament/roundrobin.html', context)
    elif tournament.tournamentType == 'SW':
        matches = Match.objects.filter(tournament=tournament).order_by('depth')
        entrants = Entrant.objects.filter(tournament=tournament).order_by('-wins')
        context = {'tournament': tournament, 'matches': matches, 'entrants': entrants}
        return render(request, 'tournament/swiss.html', context)
    return HttpResponse("Display tournament here.")

def delete(request, tournament_id):
    """ Deletes a tournament 
    """
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if tournament.owner.id == request.user.id:
        tournament.delete()
    return redirect('/')
import csv
from .models import Tournament, Match, Entrant
from django.shortcuts import get_object_or_404

def indexContext(request):
    """ Used to generate the context for the render in the index view that's used in the template
    """
    if request.user.is_authenticated:
        tournamentList = Tournament.objects.filter(owner=request.user.id).order_by('-lastUpdatedDate')
    else:
        tournamentList = None
    return {'tournamentList': tournamentList}

def createMatches(tournament):
    """ Generates the matches for each of the tournament types.
    """
    entrantList = Entrant.objects.filter(tournament=tournament).order_by('-wins')
    entrantList = list(entrantList) # converts from a QuerySet to a list so you can manipulate it easier
    if tournament.tournamentType == 'SE':
        createSEMatches(tournament, entrantList)
    elif tournament.tournamentType == 'DE':
        print("DE")
    elif tournament.tournamentType == 'RR':
        createRRMatches(tournament, entrantList)
    elif tournament.tournamentType == 'SW':
        # if entrantList is odd, add a bye by appending a None to the entrantList, making it even
        if len(entrantList) % 2 != 0:
            entrantList.append(None)
        for y in range(0, len(entrantList)//2):
            #print("doot")
            matchMade = False
            for x in range(1, len(entrantList)):
                if (entrantList
                        and not Match.objects.filter(tournament=tournament,
                            firstEntrant=entrantList[0], secondEntrant=entrantList[x]).exists()
                        and not Match.objects.filter(tournament=tournament,
                            firstEntrant=entrantList[x], secondEntrant=entrantList[0]).exists()):
                    newMatch = Match(tournament=tournament, secondEntrant=entrantList.pop(x), firstEntrant=entrantList.pop(0), depth=tournament.currentRound)
                    if newMatch.firstEntrant is None or newMatch.secondEntrant is None:
                        newMatch.winner = 4
                    newMatch.save()
                    matchMade = True
                    break
            if matchMade == False:
                break

def createSEMatches(tournament, entrantList):
    """ Generates the matches for a Single Elimination tournament, including future empty matches.
    """
    powerOfTwo = 0 # tournament brackets are based on powers of two
    # increases powerOfTwo until it fits all of the entrants
    while tournament.numberOfEntrants > 2 ** powerOfTwo:
        powerOfTwo += 1
    numberOfByes = (2 ** powerOfTwo) - tournament.numberOfEntrants # numberOfByes is the leftover amount between numberOfEntrants and 2^powerOfTwo
    # this inserts None into every other one of the starting positions for each of the byes.  means you don't have two byes matched together
    for x in range(0, numberOfByes):
        entrantList.insert(x * 2, None)
    parentlessMatches = [] # used to keep track of matches without parents.  only the final match should have no parent
    depthTrack = (2 ** powerOfTwo) // 2 # used to check against x for when the next level begins
    actualDepth = 0 # assigned to Match's depth
    # logically, in a single elimination tournament with n entrants, there are n - 1 matches, because everyone but the winner loses one match
    for x in range(0, 2 ** powerOfTwo - 1):
        # calculates the next number x has to be to increment the depth
        if x == depthTrack or x == 2 ** powerOfTwo - 2:
            depthTrack = depthTrack + (depthTrack // 2)
            actualDepth = actualDepth + 1
        # if we run out of entrants, we append two Nones to the list to fill an empty match
        if not entrantList:
            entrantList.extend((None, None))
        newMatch = Match(tournament=tournament, firstEntrant=entrantList.pop(1), secondEntrant=entrantList.pop(0), depth=actualDepth)
        # neat little xor thing!  if only one of the entrants in a match is None, then it's a bye.  otherwise, it's a future match and left unchanged
        if bool(newMatch.firstEntrant) ^ bool(newMatch.secondEntrant):
            newMatch.winner = 4
        newMatch.save()
        parentlessMatches.append(newMatch.id) # adds the newly minted match to the end of the parentlessMatches list
        # if there are id's in parentlessMatches and the first depth of matches has been created, we can start assigning parents
        # the first two parentlessMatches are assigned the last parentless match (which was just added) and popped off the list
        if parentlessMatches and x >= 2 ** powerOfTwo // 2:
            firstChild = get_object_or_404(Match, id=parentlessMatches[0])
            firstChild.parentMatch = get_object_or_404(Match, id=parentlessMatches[-1])
            firstChild.save()
            # if the child has a bye, then it's pushed forward into its parents match
            if firstChild.winner == 4:
                parent = get_object_or_404(Match, id=firstChild.parentMatch.id)
                # checks if the firstEntrant is the bye or the entrant
                if firstChild.firstEntrant:
                    # checks if there's something already in the firstEntrant of the parent
                    if not parent.firstEntrant:
                        parent.firstEntrant = firstChild.firstEntrant
                    else:
                        parent.secondEntrant = firstChild.firstEntrant
                else:
                    if not parent.firstEntrant:
                        parent.firstEntrant = firstChild.secondEntrant
                    else:
                        parent.secondEntrant = firstChild.secondEntrant
                parent.save()
            parentlessMatches.pop(0)

            secondChild = get_object_or_404(Match, id=parentlessMatches[0])
            secondChild.parentMatch = get_object_or_404(Match, id=parentlessMatches[-1])
            secondChild.save()
            # if the child has a bye, then it's pushed forward into its parents match
            if secondChild.winner == 4:
                parent = get_object_or_404(Match, id=secondChild.parentMatch.id)
                # checks if the firstEntrant is the bye or the entrant
                if secondChild.firstEntrant:
                    # checks if there's something already in the firstEntrant of the parent
                    if not parent.firstEntrant:
                        parent.firstEntrant = secondChild.firstEntrant
                    else:
                        parent.secondEntrant = secondChild.firstEntrant
                else:
                    if not parent.firstEntrant:
                        parent.firstEntrant = secondChild.secondEntrant
                    else:
                        parent.secondEntrant = secondChild.secondEntrant
                parent.save()
            parentlessMatches.pop(0)

def createRRMatches(tournament, entrantList):
    """ Generates the matches for a Round-Robin tournament.
    """
    # if entrantList is odd, add a bye by appending a None to the entrantList, making it even
    if len(entrantList) % 2 != 0:
        entrantList.append(None)
    # split entrantList in half
    firstHalfEntrant = entrantList[0:len(entrantList)//2]
    secondHalfEntrant = entrantList[len(entrantList)//2:]
    # for every possible combination
    for x in range(0, len(entrantList)-1):
        # for every matchup between the two lists
        for y in range(0, len(entrantList)//2):
            # seed is used as the round this tournament is in
            newMatch = Match(tournament=tournament, firstEntrant=firstHalfEntrant[y], secondEntrant=secondHalfEntrant[y], depth=x, winner=0)
            # if there's a bye
            if newMatch.firstEntrant is None or newMatch.secondEntrant is None:
                newMatch.winner = 4
            newMatch.save()
        secondHalfEntrant.append(firstHalfEntrant.pop())
        firstHalfEntrant.insert(1, secondHalfEntrant.pop(0))

def outputCSV(tournament):
    matchList = Match.objects.filter(tournament=tournament)
    csvFile = "id,parent,depth,entrant1id,entrant1name,entrant1wins,entrant1losses,entrant1draws,entrant2id,entrant2name,entrant2wins,entrant2losses,entrant2draws\n"
    for match in matchList:
        csvFile = ''.join([csvFile, str(match.id)])
        if match.parentMatch:
            csvFile = ','.join([csvFile, str(match.parentMatch.id)])
        else:
            csvFile = ','.join([csvFile, ''])
        csvFile = ','.join([csvFile, str(match.depth)])
        if match.firstEntrant:
            csvFile = ','.join([csvFile, str(match.firstEntrant.id),str(match.firstEntrant.name),
                str(match.firstEntrant.wins), str(match.firstEntrant.losses),str(match.firstEntrant.draws)])
        else:
            csvFile = ','.join([csvFile, '', '', '', '', ''])
        if match.secondEntrant:
            csvFile = ','.join([csvFile, str(match.secondEntrant.id),str(match.secondEntrant.name),str(match.secondEntrant.wins),
            str(match.secondEntrant.losses),str(match.secondEntrant.draws)])
        else:
            csvFile = ','.join([csvFile, '', '', '', '', ''])
        csvFile = ''.join([csvFile, '\n'])
    print(csvFile)
    return csvFile

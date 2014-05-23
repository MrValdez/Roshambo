import rps
from rps import biased_roshambo

statR = 0
statP = 0
statS = 0

denominator = 0

rockProb    = 0.0
paperProb   = 0.0
targetRock  = 0.0
targetPaper = 0.0

Debug = True
Debug = False

def calculateProbThisTurn():
    global statR, statP, statS
    global denominator
    global rockProb, paperProb, targetRock, targetPaper

    thisTurnRockProb = float((targetRock - statR) / float(denominator))
    thisTurnPaperProb = float((targetPaper - statP) / float(denominator))
    return (thisTurnRockProb, thisTurnPaperProb)

def recompute(currentTurn, targetTurn):
    global statR, statP, statS
    global denominator
    global rockProb, paperProb, targetRock, targetPaper

    rockProb = statR / float (currentTurn)
    paperProb = statP / float (currentTurn)
    
    targetRock = float(rockProb * (currentTurn + targetTurn))
    targetPaper = float(paperProb * (currentTurn + targetTurn))
    
    denominator = targetTurn


def BFP(targetTurn):
    global statR, statP, statS
    global denominator
    global rockProb, paperProb, targetRock, targetPaper

    currentTurn = rps.getTurn()
    if (currentTurn == 0):
        #initialize        
        statR, statP, statS = 0, 0, 0
        denominator = targetTurn
        rockProb = 1 / 3.0
        paperProb = 1 / 3.0
        targetRock = rockProb * targetTurn
        targetPaper = paperProb * targetTurn

        if Debug:
            print("\n\nInitial data (Target Turn %i):\n" % (targetTurn))
            print("statR, statP: %i %i" % (statR, statP));
            print("targetRock, targetPaper: %f %f" % (targetRock, targetPaper));
            print("currentTurn, denominator: %i %i" % (currentTurn, denominator))
            input()

        return biased_roshambo (1 / 3.0, 1 / 3.0)
    
    oppMove = rps.enemyHistory(currentTurn)
    
    if (oppMove == 0):
        statR += 1
    if (oppMove == 1):
        statP += 1
    if (oppMove == 2):
        statS += 1

    if (denominator <= 0):
        if Debug:
            print ("***********************")
            print ("Recomputing denominator")
            print ("***********************")
            
        recompute(currentTurn, targetTurn)
        
    thisTurnRockProb, thisTurnPaperProb = calculateProbThisTurn()
    
    if Debug:
        print("currentTurn, denominator: %i %i" % (currentTurn, denominator))
        print("statR, statP: %i %i" % (statR, statP));
        print("probR, probP:                        %f %f" % (rockProb, paperProb));
        print("targetRock, targetPaper:             %f %f" % (targetRock, targetPaper));
        print("thisTurnRockProb, thisTurnPaperProb: %f %f" % (thisTurnRockProb, thisTurnPaperProb))
        debugRecomputation = False
        
    if (thisTurnRockProb < 0 or thisTurnPaperProb < 0 or thisTurnRockProb + thisTurnPaperProb > 1.0):
        if Debug:
            debugRecomputation = True
            print ("***********************")
            print ("Recomputing because of", thisTurnRockProb <= 0, thisTurnPaperProb <= 0, thisTurnRockProb + thisTurnPaperProb >= 1.0)
            print ("***********************")
            
        recompute(currentTurn, targetTurn)
        thisTurnRockProb, thisTurnPaperProb = calculateProbThisTurn()
        
    #thisTurnRockProb = 0 if thisTurnRockProb < 0 else thisTurnRockProb
    #thisTurnPaperProb = 0 if thisTurnPaperProb < 0 else thisTurnPaperProb
    
    if Debug and debugRecomputation:
        print("targetRock, targetPaper: %f %f" % (targetRock, targetPaper));
        print("thisTurnRockProb, thisTurnPaperProb: %f %f\n" % (thisTurnRockProb, thisTurnPaperProb))
    
    if Debug:
        input()
        
    denominator -= 1
    return biased_roshambo (thisTurnRockProb, thisTurnPaperProb)

def play(targetTurn):
    move = BFP(targetTurn)
    playing = (move + 1) % 3
    if Debug:
        print("Predicting %i. Playing %i\n\n"  % (move,playing))
    return playing

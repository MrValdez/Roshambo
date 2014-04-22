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

def BFP(targetTurn):
    global statR, statP, statS
    global denominator
    global rockProb, paperProb, targetRock, targetPaper

    currentTurn = rps.getTurn()
    if (currentTurn == 0):
        #initialize
        statR = 0
        statP = 0
        statS = 0
        denominator = targetTurn
        rockProb = 1 / 3.0
        paperProb = 1 / 3.0
        targetRock = rockProb * targetTurn
        targetPaper = paperProb * targetTurn
        return biased_roshambo (1 / 3.0, 1 / 3.0)
    
    oppMove = rps.enemyHistory(currentTurn)
    
    if (oppMove == 0):
        statR += 1
    if (oppMove == 1):
        statP += 1
    if (oppMove == 2):
        statS += 1

    if (denominator <= 0):
        rockProb = statR / float(currentTurn)
        paperProb = statP / float(currentTurn)
        
        targetRock = float(rockProb * (currentTurn + targetTurn))
        targetPaper = float(paperProb * (currentTurn + targetTurn))
        
        denominator = targetTurn
        
    thisTurnRockProb = float((targetRock - statR) / float(denominator))
    thisTurnPaperProb = float((targetPaper - statP) / float(denominator))
    
    if Debug:
        print("thisTurnRockProb, thisTurnPaperProb: %f %f" % (thisTurnRockProb, thisTurnPaperProb))
        
    if (thisTurnRockProb <= 0 or thisTurnPaperProb <= 0 or thisTurnRockProb + thisTurnPaperProb >= 1.0):
        rockProb = statR / float (currentTurn)
        paperProb = statP / float (currentTurn)
        
        targetRock = float(rockProb * (currentTurn + targetTurn))
        targetPaper = float(paperProb * (currentTurn + targetTurn))
        
        denominator = targetTurn

        thisTurnRockProb = float((targetRock - statR) / float(denominator))
        thisTurnPaperProb = float((targetPaper - statP) / float(denominator))

    thisTurnRockProb = 0 if thisTurnRockProb < 0 else thisTurnRockProb
    thisTurnPaperProb = 0 if thisTurnPaperProb < 0 else thisTurnPaperProb
    
    if Debug:
        # Debug
        print("statR, targetRock: %i %f" % (statR, targetRock));
        print("statP, targetPaper: %i %f" % (statP, targetPaper));
        print("currentTurn, denominator: %i %i" % (currentTurn, denominator))
        print("thisTurnRockProb, thisTurnPaperProb: %f %f\n" % (thisTurnRockProb, thisTurnPaperProb))
        input()
        
    denominator -= 1
    return biased_roshambo (thisTurnRockProb, thisTurnPaperProb)

def play(targetTurn):
    return (BFP(targetTurn) + 1) % 3

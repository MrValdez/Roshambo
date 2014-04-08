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

Debug = False

def yomi(targetTurn):
    global statR, statP, statS
    global denominator
    global rockProb, paperProb, targetRock, targetPaper

    currentTurn = rps.myHistory(0)
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
        #input()
        
    denominator -= 1
    return (biased_roshambo (thisTurnRockProb, thisTurnPaperProb) + 1) % 3

def SkeletonAI():
    currentTurn = rps.myHistory(0)
    myMoveLastTurn = rps.myHistory(turn)
    enemyMoveLastTurn = rps.enemyHistory(turn)
    
    #input()
    return (rps.enemyHistory(turn) + 1) % 3
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    return False
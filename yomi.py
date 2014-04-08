import rps
from rps import biased_roshambo

class Situation:
    def __init__(self):
        self.statR = 0
        self.statP = 0
        self.statS = 0

        self.denominator = 0

        self.rockProb    = 0.0
        self.paperProb   = 0.0
        self.targetRock  = 0.0
        self.targetPaper = 0.0

situation = Situation()

def yomi(targetTurn):
    currentTurn = rps.myHistory(0)
    if (currentTurn == 0):
        #initialize
        situation.statR = 0
        situation.statP = 0
        situation.statS = 0
        situation.denominator = targetTurn
        situation.rockProb = 1 / 3.0
        situation.paperProb = 1 / 3.0
        situation.targetRock = situation.rockProb * targetTurn
        situation.targetPaper = situation.paperProb * targetTurn
        return biased_roshambo (1 / 3.0, 1 / 3.0)
    
    oppMove = rps.enemyHistory(currentTurn)
    
    if (oppMove == 0):
        situation.statR += 1
    if (oppMove == 1):
        situation.statP += 1
    if (oppMove == 2):
        situation.statS += 1

    if (situation.denominator <= 0):
        situation.rockProb = situation.statR / float(currentTurn)
        situation.paperProb = situation.statP / float(currentTurn)
        
        situation.targetRock = situation.rockProb * (currentTurn + targetTurn)
        situation.targetPaper = situation.paperProb * (currentTurn + targetTurn)
        
        situation.denominator = targetTurn
        
    thisTurnRockProb = (situation.targetRock - situation.statR) / float(situation.denominator)
    thisTurnPaperProb = (situation.targetPaper - situation.statP) / float(situation.denominator)
        
    if (thisTurnRockProb <= 0 or thisTurnPaperProb <= 0 or thisTurnRockProb + thisTurnPaperProb >= 1.0):
        situation.rockProb = situation.statR / float (currentTurn)
        situation.paperProb = situation.statP / float (currentTurn)
        
        situation.targetRock = situation.rockProb * (currentTurn + targetTurn)
        situation.targetPaper = situation.paperProb * (currentTurn + targetTurn)
        
        denominator = targetTurn

        thisTurnRockProb = (situation.targetRock - situation.statR) / float(situation.denominator)
        thisTurnPaperProb = (situation.targetPaper - situation.statP) / float(situation.denominator)

    thisTurnRockProb = min(0, thisTurnRockProb)
    thisTurnPaperProb = min(0, thisTurnPaperProb)
    
 #    /*    printf("statR, targetRock: %i %f\n ", statR, targetRock);
 #   printf("denominator: %i  \n", denominator);
 #   printf("thisTurnRockProb, thisTurnPaperProb: %f %f\n\n", thisTurnRockProb, thisTurnPaperProb);getch();
 #  */
 
    situation.denominator -= 1
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
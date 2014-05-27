import rps
from rps import biased_roshambo

statR = 0
statP = 0
statS = 0

remainingPredictionSize = 0

rockProb    = 0.0
paperProb   = 0.0
predictionRock  = 0.0
predictionPaper = 0.0

Debug = True
Debug = False

def calculateProbThisTurn():
    global statR, statP, statS
    global remainingPredictionSize
    global rockProb, paperProb, predictionRock, predictionPaper

    thisTurnRockProb = float((predictionRock - statR) / float(remainingPredictionSize))
    thisTurnPaperProb = float((predictionPaper - statP) / float(remainingPredictionSize))
    return (thisTurnRockProb, thisTurnPaperProb)

def recomputeFutureProb(currentTurn, targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global rockProb, paperProb, predictionRock, predictionPaper

    rockProb = statR / float (currentTurn)
    paperProb = statP / float (currentTurn)
    
    predictionRock = float(rockProb * (currentTurn + targetPredictionSize))
    predictionPaper = float(paperProb * (currentTurn + targetPredictionSize))
    
    remainingPredictionSize = targetPredictionSize


def BFP(targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global rockProb, paperProb, predictionRock, predictionPaper

    currentTurn = rps.getTurn()
    if (currentTurn == 0):
        #initialize        
        statR, statP, statS = 0, 0, 0
        remainingPredictionSize = targetPredictionSize
        rockProb = 1 / 3.0
        paperProb = 1 / 3.0
        predictionRock = rockProb * targetPredictionSize
        predictionPaper = paperProb * targetPredictionSize

        if Debug:
            print("\n\nInitial data (Target Turn %i):\n" % (targetPredictionSize))
            print("statR, statP: %i %i" % (statR, statP));
            print("predictionRock, predictionPaper: %f %f" % (predictionRock, predictionPaper));
            print("currentTurn, remainingPredictionSize: %i %i" % (currentTurn, remainingPredictionSize))
            input()

        return biased_roshambo (1 / 3.0, 1 / 3.0)
    
    oppMove = rps.enemyHistory(currentTurn)
    
    if (oppMove == 0):
        statR += 1
    if (oppMove == 1):
        statP += 1
    if (oppMove == 2):
        statS += 1

    if (remainingPredictionSize <= 0):
        if Debug:
            print ("***********************")
            print ("Recomputing remainingPredictionSize")
            print ("***********************")
            
        recomputeFutureProb(currentTurn, targetPredictionSize)
        
    thisTurnRockProb, thisTurnPaperProb = calculateProbThisTurn()
    
    if Debug:
        print("currentTurn, remainingPredictionSize: %i %i" % (currentTurn, remainingPredictionSize))
        print("statR, statP: %i %i" % (statR, statP));
        print("probR, probP:                        %f %f" % (rockProb, paperProb));
        print("predictionRock, predictionPaper:             %f %f" % (predictionRock, predictionPaper));
        print("thisTurnRockProb, thisTurnPaperProb: %f %f" % (thisTurnRockProb, thisTurnPaperProb))
        debugRecomputation = False
        
    if (thisTurnRockProb < 0 or thisTurnPaperProb < 0 or thisTurnRockProb + thisTurnPaperProb > 1.0):
        if Debug:
            debugRecomputation = True
            print ("***********************")
            print ("Recomputing because of", thisTurnRockProb <= 0, thisTurnPaperProb <= 0, thisTurnRockProb + thisTurnPaperProb >= 1.0)
            print ("***********************")
            
        recomputeFutureProb(currentTurn, targetPredictionSize)
        thisTurnRockProb, thisTurnPaperProb = calculateProbThisTurn()
        
    #thisTurnRockProb = 0 if thisTurnRockProb < 0 else thisTurnRockProb
    #thisTurnPaperProb = 0 if thisTurnPaperProb < 0 else thisTurnPaperProb
    
    if Debug and debugRecomputation:
        print("predictionRock, predictionPaper: %f %f" % (predictionRock, predictionPaper));
        print("thisTurnRockProb, thisTurnPaperProb: %f %f\n" % (thisTurnRockProb, thisTurnPaperProb))
    
    if Debug:
        input()
        
    remainingPredictionSize -= 1
    return biased_roshambo (thisTurnRockProb, thisTurnPaperProb)

def play(targetPredictionSize):
    move = BFP(targetPredictionSize)
    playing = (move + 1) % 3
    if Debug:
        print("Predicting %i. Playing %i\n\n"  % (move,playing))
    return playing

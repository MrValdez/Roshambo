import rps
from rps import biased_roshambo

statR = 0
statP = 0
statS = 0

remainingPredictionSize = 0

probRock    = 0.0
probPaper   = 0.0
predictionRock  = 0.0
predictionPaper = 0.0

Debug = True
Debug = False

def calculateProbThisTurn():
    global statR, statP, statS
    global remainingPredictionSize
    global probRock, probPaper, predictionRock, predictionPaper

    thisTurnProbRock = float((predictionRock - statR) / float(remainingPredictionSize))
    thisTurnProbPaper = float((predictionPaper - statP) / float(remainingPredictionSize))
    
    return (thisTurnProbRock, thisTurnProbPaper)

def recomputeFutureProb(currentTurn, targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global probRock, probPaper, predictionRock, predictionPaper

    probRock = statR / float (currentTurn)
    probPaper = statP / float (currentTurn)
    
    predictionRock = float(probRock * (currentTurn + targetPredictionSize))
    predictionPaper = float(probPaper * (currentTurn + targetPredictionSize))
    
    remainingPredictionSize = targetPredictionSize


def BFP(targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global probRock, probPaper, predictionRock, predictionPaper

    currentTurn = rps.getTurn()
    if (currentTurn == 0):
        #initialize        
        statR, statP, statS = 0, 0, 0
        remainingPredictionSize = targetPredictionSize
        probRock = 1 / 3.0
        probPaper = 1 / 3.0
        predictionRock = probRock * targetPredictionSize
        predictionPaper = probPaper * targetPredictionSize

        if Debug:
            print("\n\nInitial data (Target Prediction Size %i):\n" % (targetPredictionSize))
            print("statR, statP:                         %i    %i" % (statR, statP));
            print("predictionRock, predictionPaper:      %.2f %.2f" % (predictionRock, predictionPaper));
            print("currentTurn, remainingPredictionSize: %i    %i" % (currentTurn, remainingPredictionSize))
            print("Done init()\n")

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
        
    thisTurnProbRock, thisTurnProbPaper = calculateProbThisTurn()
    
    if Debug:
        print("currentTurn, remainingPredictionSize: %i    %i" % (currentTurn, remainingPredictionSize))
        print("statR, statP:                         %i    %i" % (statR, statP));
        print("probR, probP:                         %.2f %.2f" % (probRock, probPaper));
        print("predictionRock, predictionPaper:      %.2f %.2f" % (predictionRock, predictionPaper));
        print("thisTurnProbRock, thisTurnProbPaper:  %.2f %.2f" % (thisTurnProbRock, thisTurnProbPaper))
        debugRecomputation = False
        
    if (thisTurnProbRock < 0 or thisTurnProbPaper < 0 or thisTurnProbRock + thisTurnProbPaper > 1.0):
        if Debug:
            debugRecomputation = True
            print ("***********************")
            print ("Recomputing because of", thisTurnProbRock <= 0, thisTurnProbPaper <= 0, thisTurnProbRock + thisTurnProbPaper >= 1.0)
            
        recomputeFutureProb(currentTurn, targetPredictionSize)
        thisTurnProbRock, thisTurnProbPaper = calculateProbThisTurn()

    #thisTurnProbRock = 0 if thisTurnProbRock < 0 else thisTurnProbRock
    #thisTurnProbPaper = 0 if thisTurnProbPaper < 0 else thisTurnProbPaper
    
    if Debug and debugRecomputation:
        print("New recomputation:")
        print("predictionRock, predictionPaper:      %.2f %.2f" % (predictionRock, predictionPaper));
        print("thisTurnProbRock, thisTurnProbPaper:  %.2f %.2f\n" % (thisTurnProbRock, thisTurnProbPaper))
        input()
    
    if Debug:
        input()
        
    remainingPredictionSize -= 1
    return biased_roshambo (thisTurnProbRock, thisTurnProbPaper)

def play(targetPredictionSize):
    move = BFP(targetPredictionSize)
    playing = (move + 1) % 3
    if Debug:
        print("Predicting %i. Playing %i\n\n"  % (move,playing))
    return playing

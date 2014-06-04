import rps
from rps import biased_roshambo

statR = 0
statP = 0
statS = 0

remainingPredictionSize = 0

probR = 0.0
probP = 0.0
predictionR = 0.0
predictionP = 0.0

Debug = True
Debug = False

def calculateProbThisTurn():
    global statR, statP, statS
    global remainingPredictionSize
    global probR, probP, predictionR, predictionP

    thisTurnProbR = float((predictionR - statR) / float(remainingPredictionSize))
    thisTurnProbP = float((predictionP - statP) / float(remainingPredictionSize))
    
    return (thisTurnProbR, thisTurnProbP)

def recomputeFutureProb(currentTurn, targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global probR, probP, predictionR, predictionP

    probR = statR / float (currentTurn)
    probP = statP / float (currentTurn)
    
    predictionR = float(probR * (currentTurn + targetPredictionSize))
    predictionP = float(probP * (currentTurn + targetPredictionSize))
    
    remainingPredictionSize = targetPredictionSize


def BFP(targetPredictionSize):
    global statR, statP, statS
    global remainingPredictionSize
    global probR, probP, predictionR, predictionP

    currentTurn = rps.getTurn()
    if (currentTurn == 0):
        #initialize        
        statR, statP, statS = 0, 0, 0
        remainingPredictionSize = targetPredictionSize
        probR = 1 / 3.0
        probP = 1 / 3.0
        predictionR = probR * targetPredictionSize
        predictionP = probP * targetPredictionSize

        if Debug:
            print("\n\nInitial data (Target Prediction Size %i):\n" % (targetPredictionSize))
            print("statR, statP:                         %i    %i" % (statR, statP));
            print("predictionR, predictionP:             %.2f %.2f" % (predictionR, predictionP));
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
        
    thisTurnProbR, thisTurnProbP = calculateProbThisTurn()
    
    if Debug:
        print("currentTurn, remainingPredictionSize: %i    %i" % (currentTurn, remainingPredictionSize))
        print("statR, statP:                         %i    %i" % (statR, statP));
        print("probR, probP:                         %.2f %.2f" % (probR, probP));
        print("predictionR, predictionP:             %.2f %.2f" % (predictionR, predictionP));
        print("thisTurnProbR, thisTurnProbP:         %.2f %.2f" % (thisTurnProbR, thisTurnProbP))
        debugRecomputation = False
        
    if (thisTurnProbR < 0 or thisTurnProbP < 0 or thisTurnProbR + thisTurnProbP > 1.0):
        if Debug:
            debugRecomputation = True
            print ("***********************")
            print ("Recomputing because of", thisTurnProbR <= 0, thisTurnProbP <= 0, thisTurnProbR + thisTurnProbP >= 1.0)
            print ("***********************")
            
        recomputeFutureProb(currentTurn, targetPredictionSize)
        thisTurnProbR, thisTurnProbP = calculateProbThisTurn()

    # These two checks will never be True as proven by studying the algorithm. 
    # But in the interest of keeping this program bug free (and for the sanity of the coder), they are added
    thisTurnProbR = 0 if thisTurnProbR < 0 else thisTurnProbR
    thisTurnProbP = 0 if thisTurnProbP < 0 else thisTurnProbP
    
    if Debug and debugRecomputation:
        print("predictionR, predictionP:             %.2f %.2f" % (predictionR, predictionP));
        print("thisTurnProbR, thisTurnProbP:         %.2f %.2f\n" % (thisTurnProbR, thisTurnProbP))
    
    if Debug:
        input()
        
    remainingPredictionSize -= 1
    return biased_roshambo (thisTurnProbR, thisTurnProbP)

def play(targetPredictionSize):
    move = BFP(targetPredictionSize)
    playing = (move + 1) % 3
    if Debug:
        print("Predicting %i. Playing %i\n\n"  % (move,playing))
    return playing

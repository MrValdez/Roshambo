import BeatFrequentPick
import rps
Debug = True
Debug = False

yomiScore = [0, 0, 0, 0]
yomiChoices = [0, 0, 0, 0]
layerLastTurn = 0

def init():
    yomiScore = [0, 0, 0, 0]
    layerLastTurn = 0

def yomi(prediction):
    global yomiScore
    global layerLastTurn 

    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init()
    else:
        # update score from last turn
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == enemyMoveLastTurn + 1)
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        
        if victory:
            scoreThisTurn = 2
        elif tie:
            scoreThisTurn = 1
        else:
            scoreThisTurn = -1
        
        #for i in range(4):
        #    if yomiScore[i] == myMoveLastTurn: yomiScore[i] += scoreThisTurn
        yomiScore[layerLastTurn] += scoreThisTurn

    # fill up yomiChoices with the moves to be played
    yomiChoices = []
    yomiChoices.append(rps.random() % 3)        # layer 0   (original choice
    yomiChoices.append((prediction + 1) % 3)  # layer 1   (beats enemy's choice)
    yomiChoices.append((prediction + 2) % 3)  # layer 2   (beats enemy's layer 1)
    yomiChoices.append((prediction + 3) % 3)  # layer 3   (beats enemy's layer 2)
    
#    print (yomiChoices)

    # figure out what layer to use
    # 1. Get the highest point
    # 2. Get all the layers with the same points
    # 3. randomize what layer to choose amongst top ranking
    maxPoint = max(yomiScore)
    topLayersCount = yomiScore.count(maxPoint)
    
    probDistribution = 1.0 / topLayersCount        # can be changed to a subsystem
    chances = []
    currentCount = 1
    for i in range(4):
        if yomiScore[i] == maxPoint: 
            chances.append(probDistribution * currentCount)
            currentCount += 1
        else:
            chances.append(0)    
#    print (chances)
    
    value = rps.randomRange()
    layerToUse = 0
    for i in range(4):
        if value <= chances[i]: 
            layerToUse = i
            break
    
    layerLastTurn = layerToUse
        
    # return move based on layer
    move = yomiChoices[layerToUse]
#    input()
    return move
    
def play(a):
    prediction = BeatFrequentPick.play(a)
    decision = yomi(prediction)
    return decision


def SkeletonAI():
    """ This is the most basic AI that shows the functions used """
    currentTurn = rps.getTurn()
    
    if currentTurn:
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        
    print ("%i" % (currentTurn))
    print (" %i %i" % (rps.myHistory(currentTurn - 0), rps.enemyHistory(currentTurn - 0)))
    print (" %i %i" % (rps.myHistory(currentTurn - 1), rps.enemyHistory(currentTurn - 1)))
    
    input()
    return (rps.enemyHistory(currentTurn) + 1) % 3
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    global Debug
    return Debug
        
def BeatFrequentPickAI(a):
    import BeatFrequentPick
    return BeatFrequentPick.play(a)

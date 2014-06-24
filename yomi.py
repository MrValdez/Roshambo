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
    global yomiChoices
    global layerLastTurn 

    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init()
    else:
        # update score from last turn
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        
        if victory:
            scoreThisTurn = 2
            yomiScore[layerLastTurn] += scoreThisTurn
        elif tie:
            scoreThisTurn = 1
            yomiScore[layerLastTurn] += scoreThisTurn
        else:
            # add score to yomi layer that would have gave us a win
            scoreThisTurn = 2
            
            winningMove = (enemyMoveLastTurn + 1) % 3
            # search for the layer that contains the winning move
            for i in range(1, len(yomiScore)):
                if yomiChoices[i] == winningMove:
                    yomiScore[i] += scoreThisTurn
                    break
        
        #for i in range(1, len(yomiScore)):
        #    if yomiChoices[i] == myMoveLastTurn: yomiScore[i] += scoreThisTurn
        

    # fill up yomiChoices with the moves to be played
    layer0 = rps.random() % 3          # layer 0   (original choice)
    layer1 = (prediction + 1) % 3      # layer 1   (beats enemy's choice)
    layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
    layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
    
    yomiChoices = []
    yomiChoices.append(layer0)        
    yomiChoices.append(layer1)        
    yomiChoices.append(layer2)        
    yomiChoices.append(layer3)        
    
    if Debug: print ("Yomi Choices: " + str(yomiChoices))

    # figure out what layer to use
    # 1. Get the highest point
    # 2. Get all the layers with the same points
    # 3. randomize what layer to choose amongst top ranking
    maxPoint = max(yomiScore)
    topLayersCount = yomiScore.count(maxPoint)
    
    probDistribution = 1.0 / topLayersCount        # can be changed to a subsystem
    if Debug: print (probDistribution)
    chances = []
    currentCount = 1
    for i in range(1, 4):
        if yomiScore[i] == maxPoint: 
            chances.append(probDistribution * currentCount)
            currentCount += 1
        else:
            chances.append(0)    
    if Debug: print ("Yomi Score: " + str(yomiScore))
    if Debug: print ("Chances:    " + str(chances))
    
    value = rps.randomRange()
    layerToUse = 0
    for i in range(len(chances)):
        if value <= chances[i]: 
            layerToUse = i
            layerToUse += 1     # do this because layer 0 is removed.
            break
    if Debug: print ("Using layer %i. Random value was %f" % (layerToUse, value))
    layerLastTurn = layerToUse
    
    if Debug: input()
    
    # return move based on layer
    move = yomiChoices[layerToUse]
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

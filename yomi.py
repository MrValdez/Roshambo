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
        else:
            if tie:
                scoreThisTurn = 2
            else:
                scoreThisTurn = -1
                yomiScore[layerLastTurn] += scoreThisTurn
                
            scoreThisTurn = 1
            
            # add score to yomi layer that would have gave us a win
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
    
    yomiChoices = [layer0, layer1, layer2, layer3]
    
    if Debug: print ("Yomi Choices: " + str(yomiChoices))

    # figure out what layer to use
    # 1. Get the sum of all the score
    # 2. Get the ratio for each layer
    # 3. randomize what layer to choose amongst top ranking
    yomiScoreSum = 0
    for score in yomiScore:
        if score > 0:
            yomiScoreSum += score
            
    if yomiScoreSum == 0:
        chances = [1/3, 1/3 * 2, 1.0]
    else:
        chances = []
        currentCount = 1
        prevRatio = 0
        for i in range(1, 4):
            if yomiScore[i] > 0:
                ratio = prevRatio + (yomiScore[i] / yomiScoreSum)
                chances.append(ratio)
                prevRatio = ratio
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

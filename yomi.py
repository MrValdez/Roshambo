#todo:
# make chances for each yomi layer different (not 1/3 each)

import BeatFrequentPick
import rps
Debug = True
#Debug = False

yomiScore = [0, 0, 0, 0]
yomiChoices = [0, 0, 0, 0]
layerLastTurn = 0

currentOpponent = 0

class YomiData:
    def __init__(self):
        self.loadDefault()
        self.loadData()
        
    def loadDefault(self):
        # defaults:
        self.victoryDelta = 1           # change to score when layer wins
        self.lostDelta = -1             # change to score when layer lost
        self.tieDelta = 0               # change to score when layer tied
        self.winningDeltaForLost = 2    # change to the layer score which should have won (if choice lost)
        self.winningDeltaForTie = 1     # change to the layer score which should have won (if choice tied)
        self.decayDelta = [1.0, 1.0, 1.0, 1.0] # changes to the layer scores every turn by multiplication (different layers have different decay scores)       

    def loadData(self):
        self.victoryDelta = 1
        self.lostDelta = -1
        self.tieDelta = 0
        self.winningDeltaForLost = 2
        self.winningDeltaForTie = 1
        self.decayDelta = [1.0, 1.0, 1.0, 1.0]
        self.decayDelta = [1.0, 0.9, 0.8, 0.1]
        
YomiData = YomiData()

def init():
    global yomiScore
    global layerLastTurn 
    yomiScore = [0, 0, 0, 0]
    layerLastTurn = 0
    
def prettifyList(list):
    #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
    return str(["%0.2f" % i for i in list])[1:-1].replace("'", "").rjust(25)

def updateScore():
    # update score from last turn
    global yomiScore
    global yomiChoices
    global layerLastTurn
    
    currentTurn = rps.getTurn()

    myMoveLastTurn = rps.myHistory(currentTurn)
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)
    victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
    tie = (myMoveLastTurn == enemyMoveLastTurn)

    # decay the scores
    for i in range(len(yomiScore)):
        yomiScore[i] *= YomiData.decayDelta[i]
        if yomiScore[i] < 0: yomiScore[i] = 0

    if victory:
        scoreThisTurn = YomiData.victoryDelta
        yomiScore[layerLastTurn] += scoreThisTurn
    else:
        if tie:
            yomiScore[layerLastTurn] += YomiData.tieDelta
            scoreThisTurn = YomiData.winningDeltaForTie
        else:
            yomiScore[layerLastTurn] += YomiData.lostDelta
            scoreThisTurn = YomiData.winningDeltaForLost
        
        # add score to yomi layer that would have gave us a win
        winningMove = (enemyMoveLastTurn + 1) % 3
        
        # search for the layer that contains the winning move
        for i in range(1, 4):
            if yomiChoices[i] == winningMove:
                yomiScore[i] += scoreThisTurn
                break

    for i in range(len(yomiScore)):
        if yomiScore[i] < 0: yomiScore[i] = 0
    
def decideYomiLayer(yomiScore):
    # figure out what layer to use
    # 1. Get the sum of all the score
    # 2. Get the ratio for each layer
    # 3. randomize what layer to choose amongst top ranking
    yomiScoreSum = 0
    for i in range(1, 4):
        score = yomiScore[i]
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
                
    if Debug: print ("Yomi Score:  " + prettifyList(yomiScore))
    if Debug: print ("Chances:     " + prettifyList(chances))
    if Debug: 
        chanceSize = [chances[0], chances[1] - chances[0]]
        if chances[1] > 0 and chances[2] > 0:
            chanceSize.append(chances[2] - chances[1])
        elif chances[2] == 0:
            chanceSize.append(0)
            chanceSize[1] = 0
        else:
            chanceSize.append(chances[2] - chances[0])
            chanceSize[1] = 0
            
        print ("Chances Size:" + prettifyList(chanceSize))
   
    value = rps.randomRange()
    layerToUse = 0
    for i in range(len(chances)):
        if value <= chances[i]: 
            layerToUse = i
            layerToUse += 1     # do this because layer 0 is removed.
            break
    
    if Debug: print ("Random value was %f." % (value))

    #experiment
#    currentMax = 0
#    layerToUse = 1
#    for i in range(1, len(chances) + 1):
#        if yomiScore[i] > currentMax:
#            currentMax = yomiScore[i]
#            layerToUse = i
    #experiment        
    
    return layerToUse

def yomi(prediction):
    global yomiScore
    global yomiChoices
    global currentOpponent
    global layerLastTurn
    
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init()

        # This code is for jumping into a specific opponent for debugging
        if currentOpponent == 1:
            global Debug
#            Debug = True
        currentOpponent += 1
    else:
        updateScore()

    # fill up yomiChoices with the moves to be played
    layer0 = rps.random() % 3          # layer 0   (original choice)
    layer1 = (prediction + 1) % 3      # layer 1   (beats enemy's choice)
    layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
    layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
    
    yomiChoices = [layer0, layer1, layer2, layer3]
    
    if Debug: print ("Yomi Choices:      %i     %i     %i     %i" % (yomiChoices[0], yomiChoices[1], yomiChoices[2], yomiChoices[3]))

    layerToUse = decideYomiLayer(yomiScore)
    layerLastTurn = layerToUse
    
    if Debug: print ("Using layer %i." % (layerToUse))    
    
    # return move based on layer
    move = yomiChoices[layerToUse]
    return move
    
def play(a):
    if Debug:
        if rps.getTurn() == 0: 
            print("\n\n")
        else:             
            input()

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
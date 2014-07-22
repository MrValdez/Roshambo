#todo:
# make chances for each yomi layer different (not 1/3 each)

# make switching layers contain a cost. going higher has a higher cost. going lower has a lower cost. (this is modelling confidence)

# yomi = we are modelling what layer the opponent is susceptible to
# changing layer = we are modelling how confident we are that the opponent did not decide to change layer. In future AIs, if the opponent did something unexpected, this has a larger chance to flip.

# perlin noise instead of random?

import math
import BeatFrequentPick
import rps
Debug = True
Debug = False

yomiChoices = [0, 0, 0, 0]
layerLastTurn = 0

# for debugging
yomiLayerUsage = [0, 0, 0, 0]        # Count how many times a yomi layer is used
yomiLayerScore = [0, 0, 0, 0]        # Count how many times a yomi layer won

currentOpponent = 0

class YomiData:
    def __init__(self):
        self.loadDefault()
        self.loadData()
        
    def updateScore(self):
        # update score from last turn
        global yomiChoices
        global layerLastTurn
        
        currentTurn = rps.getTurn()
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        
        # decay the scores
        for i in range(len(self.yomiScore)):
            self.yomiScore[i] *= self.decayDelta[i]
            if self.yomiScore[i] < 0: self.yomiScore[i] = 0

        if victory:
            self.yomiScore[layerLastTurn] += self.victoryDelta * self.layerPreference[i]
            self.confidence += 3
            
            yomiLayerScore[layerLastTurn] += 1
        else:
            if tie:
                self.yomiScore[layerLastTurn] += self.tieDelta * self.layerPreference[i]
                scoreThisTurn = self.winningDeltaForTie
                self.confidence -= 1
            else:
                self.yomiScore[layerLastTurn] += self.lostDelta * self.layerPreference[i]
                scoreThisTurn = self.winningDeltaForLost
                self.confidence -= 2
            
            # add score to yomi layer that would have gave us a win
            winningMove = (enemyMoveLastTurn + 1) % 3
            
            # search for the layer that contains the winning move
            for i in range(1, 4):
                if yomiChoices[i] == winningMove:
                    self.yomiScore[i] +=  scoreThisTurn * self.layerPreference[i]
                    break

        if self.confidence < 0:                  self.confidence = 0
        if self.confidence > self.maxConfidence: self.confidence = self.maxConfidence

        for i in range(len(self.yomiScore)):
            if self.yomiScore[i] < 0: self.yomiScore[i] = 0

        if victory:
            self.observation -= self.observationDeltaForWin
        elif tie:
            self.observation -= self.observationDeltaForTie
        else:
            self.observation -= self.observationDeltaForLost
        
    def loadDefault(self):
        # defaults:            
        self.yomiScore = [0, 0, 0, 0]   
        self.victoryDelta = 1           # change to score when layer wins
        self.lostDelta = -1             # change to score when layer lost
        self.tieDelta = 0               # change to score when layer tied
        self.winningDeltaForLost = 2    # change to the layer score which should have won (if choice lost)
        self.winningDeltaForTie = 1     # change to the layer score which should have won (if choice tied)
        self.decayDelta = [1.0, 1.0, 1.0, 1.0] # changes to the layer scores every turn by multiplication (different layers have different decay scores)
        
        self.layerPreference = [0, 1, 0.9, 0.1]    # how much is added to each layer when adding delta
        self.confidence = 0
        self.maxConfidence = 10
        
        self.observation = 15
        self.observationDeltaForLost = 3
        self.observationDeltaForTie = 2
        self.observationDeltaForWin = 1
        self.layerConfidenceTresholdDuringObservationMode = 0.7

    def loadData(self):
        self.decayDelta = [1.0, 0.9, 0.8, 0.7]
        
YomiData = YomiData()

def init():
    global layerLastTurn 
    layerLastTurn = 0
    
    YomiData.__init__()
    
    global yomiChoices, yomiLayerUsage
    yomiChoices = [0, 0, 0, 0]
    yomiLayerUsage = [0, 0, 0, 0]        # Count how many times a yomi layer is used
    yomiLayerScore = [0, 0, 0, 0]        # Count how many times a yomi layer won
    
def prettifyList(list):
    #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
    return str(["%0.2f" % i for i in list])[1:-1].replace("'", "").rjust(25)

def debugYomiStatUsage():
    return
    print ("\n\nYomi stats:  " + str(yomiLayerUsage))
    print ("Score stats: " + str(yomiLayerScore))
    print ("\n")
    
import csv
    
def shouldChangeLayer(X, confidenceGraph, originLayer, targetLayer, confidenceCeiling = 0.7):
    """ 
    Returns [True or False, confidence level]
    
    confidenceGraph should be ([one dimensional array], [(layer1_start, layer1_end), (layer2_start, layer2_end), (layer3_start, layer3_end))
    
    Init:
        Normalize confidenceGraph to confidenceCeiling (todo)
    
    This function check where X lies in the confidenceGraph.
    1. If the target layer is higher than the origin layer,
        a. target = Find the max of next layer.
        b. result = Check if X is equal or exceeds the target.
       If the target layer is lower than the origin layer,. 
        a. target = Find the min of next layer.
        b. result = Check if X is equal or lower the target.
    
    3. return result
    
    Sample confidence graph:
    
    L1|  |L3 
    ....../.
    ...../..
    ..../...
    .../....
    ../.....
    ./......
    /.......
      |L2|  
    
    """
    
    layersRange = confidenceGraph[1]
    
    # normalize confidenceGraph
    confidenceGraphMax = max(confidenceGraph[0])
    # normalize confidenceGraph against confidenceCeiling
    #confidenceGraphMax += int(confidenceGraphMax * confidenceCeiling)
    confidenceGraphChart = [(x / confidenceGraphMax) * confidenceCeiling for x in confidenceGraph[0]]    

    saveGraph = False
    if saveGraph:
        # todo:
        with open('foo.csv', 'w') as f:
            # layer range
            #todo
            # layer data
            for i in confidenceGraphChart:
                s = "%.2f\n" % (i)
                f.write(s)
            
        print ("log saved")
        input()
    
    if originLayer > targetLayer:
        op = min
    else:
        op = max
        
    targetStart = layersRange[targetLayer][0]
    targetEnd   = layersRange[targetLayer][1]
    targetStart = int(targetStart)
    targetEnd   = int(targetEnd)
    layerGraph  = confidenceGraphChart[targetStart:targetEnd]
    
    target      = op(layerGraph)
    result      = X > target
    if originLayer < targetLayer:
        confidenceLevel = target - X
    else:
        confidenceLevel = X - target
    
    return result, confidenceLevel
    
def decideYomiLayer(yomiScore):
    # figure out what layer to use
    # 1. Get the sum of all the score
    # 2. Get the ratio for each layer
    # 3. If we are still under observation mode, don't use yomi, but keep score
    # 4. If we are, randomize what layer to choose amongst top ranking
        
    yomiScoreSum = 0
    for i in range(1, 4):
        score = yomiScore[i]
        if score > 0:
            yomiScoreSum += score
            
    if yomiScoreSum == 0:
        chances = [1/3, 2/3, 1.0]
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

    chanceSize = [chances[0], chances[1] - chances[0]]      # chanceSize tells us how big the layer's ratio is
    if chances[1] > 0 and chances[2] > 0:
        chanceSize.append(chances[2] - chances[1])
    elif chances[2] == 0:
        chanceSize.append(0)
        chanceSize[1] = 0
    else:
        chanceSize.append(chances[2] - chances[0])
        chanceSize[1] = 0

    if Debug: 
        print ("Yomi Score:  " + prettifyList(yomiScore))
        print ("Chances:     " + prettifyList(chances))            
        print ("Chances Size:" + prettifyList(chanceSize))
            
    layerConfidence = 0  # how confident we are with our layer choice
    value = rps.randomRange()
    layerToUse = 0
    for i in range(len(chances)):
        if value <= chances[i]: 
            layerToUse = i
            layerToUse += 1     # do this because layer 0 is removed.
            
            total = 0
            for j in range(0, i):
                total += chanceSize[j]
                
            layerConfidence = value - total
            if layerConfidence < 0: layerConfidence = 0
            break
    
    if Debug: print ("Random value was %f." % (value))

    # while in observation mode, use layer 0 except when the layer we have chosen passes the treshold.
    if YomiData.observation > 0:
        if Debug: print ("***Currently in observation mode***")
        
        if chances[layerToUse - 1] > YomiData.layerConfidenceTresholdDuringObservationMode:
            if Debug: 
                print ("Layer Confidence Treshold reached even when under observation mode.")
                print ("Treshold: %.2f" % (YomiData.layerConfidenceTresholdDuringObservationMode))
        else:
            layerToUse = 0

    return layerToUse, layerConfidence

def getYomiChoices(prediction):    
    global yomiChoices

    # fill up yomiChoices with the moves to be played
    layer0 = rps.random() % 3          # layer 0   (original choice)
    layer1 = (prediction + 1) % 3      # layer 1   (beats enemy's choice)
    layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
    layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
    
    yomiChoices = [layer0, layer1, layer2, layer3]

    if Debug: print ("Yomi Choices:      %i     %i     %i     %i" % 
                     (yomiChoices[0], yomiChoices[1], yomiChoices[2], yomiChoices[3]))

    return yomiChoices

def yomi(prediction):
    global currentOpponent
    global layerLastTurn
    
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init()
    else:
        YomiData.updateScore()
        
    if currentTurn == 999:
        debugYomiStatUsage()

        # This code is for jumping into a specific opponent for debugging
        currentOpponent += 1
        if currentOpponent == 1:
            global Debug
            #Debug = True
    
    yomiChoices = getYomiChoices(prediction)
    
    layerToUse, layerConfidence = decideYomiLayer(YomiData.yomiScore)
    
    # see if we are confident with changing layers
    if layerLastTurn > 0 and layerLastTurn != layerToUse:
        if YomiData.confidence == 1:
            # we are confident to stay in this layer
            layerToUse = layerLastTurn
        else:
            # see if we should change layer
            flipValue = rps.randomRange()
            layerSize = [10, 30, 70]        # end of layer1, end of layer2, end of layer3
            layerRange = [(0, layerSize[0])] 
            layerRange.append((layerRange[0][1], layerSize[1]))
            layerRange.append((layerRange[1][1], layerSize[2]))
            confidenceGraph = ([x for x in range(100)], layerRange)
            #confidenceGraph = ([math.log(x+0.1) for x in range(100)], layerRange)
                                 
            changeLayer, confidence = shouldChangeLayer(flipValue, confidenceGraph, layerLastTurn - 1, layerToUse - 1)

            if changeLayer == False:
                if Debug:
                    print ("Layer did not change from %i to %i.\n AI's confidence: %.2f. Missing confidence: %.2f" % 
                            (layerLastTurn, layerToUse, flipValue, confidence))
                    
                layerToUse = layerLastTurn
                    
    layerLastTurn = layerToUse
    
    if Debug: print ("Using layer %i." % (layerToUse))    

    yomiLayerUsage[layerToUse] += 1
    
    # return move based on layer
    move = yomiChoices[layerToUse]
    return move
    
def play(a):
    if Debug:
        if rps.getTurn() == 0: 
            print("\n\n")
        else:             
            if not YomiData.observation > 0:    # skip to the point when we are no longer observing
                input()
            else:
                print()

    prediction = BeatFrequentPick.play(a)
    decision = yomi(prediction)
    return decision
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    global Debug
    return Debug
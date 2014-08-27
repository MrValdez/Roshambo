# priority:
# temporarily remove decision making for benchmarking purposes

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

yomiChoices = [0, 0, 0]
layerLastTurn = 0

# for debugging
yomiLayerUsage = [0, 0, 0]        # Count how many times a yomi layer is used
yomiLayerScore = [0, 0, 0]        # Count how many times a yomi layer won

currentOpponent = 0

class YomiPersonality:
    """ contains the personality that can influence what yomi layers to use """
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
        self.decayDelta = [1.0, 1.0, 1.0] # changes to the layer scores every turn by multiplication (different layers have different decay scores)
        self.minimumLayerConsideration = 0.0    # the lowest probability that a layer can have
        
        self.layerPreference = [1, 0.9, 0.1]    # how much is added to each layer when adding delta
        
        # observation mode is when the Yomi AI studies the opponent first
        self.observation = 15                       # initial observation point
        self.observationDeltaForLost = 3
        self.observationDeltaForTie = 2
        self.observationDeltaForWin = 1
        self.layerConfidenceTresholdDuringObservationMode = 0.7

        self.layerConfidenceSize = [10, 30, 0]        # how large the AI's confidence is with each layer. Its possible to not have 100% confidence
        
    def loadData(self):
        self.decayDelta = [0.9, 0.8, 0.7]
    
        # experiment
        self.layerPreference = [1, 1, 1] 
        self.observation = 0
        self.decayDelta = [1, 1, 1]
        self.winningDeltaForLost = 1.5
        self.winningDeltaForTie = 1
        self.minimumLayerConsideration = 0.1
        
class YomiData:
    def __init__(self):
        personality = YomiPersonality()
        self.__dict__ = personality.__dict__.copy()

        self.yomiScore = [0, 0, 0]   
        
        # AI's localize confidence
        # todo: implement this
        self.confidence = 0
        self.maxConfidence = 10
        
        
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

        if self.observation or layerLastTurn != -1:
            if victory:
                self.yomiScore[layerLastTurn] += self.victoryDelta * self.layerPreference[layerLastTurn]
                self.confidence += 3
                
                yomiLayerScore[layerLastTurn] += 1
            else:
                if tie:
                    self.yomiScore[layerLastTurn] += self.tieDelta * self.layerPreference[layerLastTurn]
                    scoreThisTurn = self.winningDeltaForTie
                    self.confidence -= 1
                else:
                    self.yomiScore[layerLastTurn] += self.lostDelta * self.layerPreference[layerLastTurn]
                    scoreThisTurn = self.winningDeltaForLost
                    self.confidence -= 2
                
                # add score to yomi layer that would have gave us a win
                winningMove = (enemyMoveLastTurn + 1) % 3
                
                # search for the layer that contains the winning move and update it
                for i in range(len(yomiChoices)):
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
        
        
YomiData = YomiData()

def init():
    global layerLastTurn 
    layerLastTurn = 0
    
    YomiData.__init__()
    
    global yomiChoices, yomiLayerUsage
    yomiChoices = [0, 0, 0]
    yomiLayerUsage = [0, 0, 0]        # Count how many times a yomi layer is used
    yomiLayerScore = [0, 0, 0]        # Count how many times a yomi layer won
    
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
            s = [str(s[1]) for s in layersRange]
            f.write(",".join(s))
            f.write("\n")
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
        
    graphSize   = len(confidenceGraphChart)
    targetStart = layersRange[targetLayer][0]
    targetEnd   = layersRange[targetLayer][1]
    targetStart = int(targetStart)
    targetEnd   = int(targetEnd)
    targetStart = min(targetStart, graphSize)          # make sure we don't go outside the graph
    targetEnd   = min(targetEnd, graphSize)            # make sure we don't go outside the graph
    layerGraph  = confidenceGraphChart[targetStart:targetEnd]
    
    if len(layerGraph) <= 0:
        return False, 0
        
    target      = op(layerGraph)
    result      = X > target
    if originLayer < targetLayer:
        confidenceLevel = target - X
    else:
        confidenceLevel = X - target
    
    return result, confidenceLevel

def decideChangeLayer(YomiData, layerToUse, layerConfidence, layerLastTurn):    
    # see if we are confident with changing layers
    if (layerToUse != -1 and layerLastTurn  != -1) and layerLastTurn != layerToUse:
        if YomiData.confidence > 5:
            # we are confident to stay in this layer
            layerToUse = layerLastTurn
        else:
            # see if we should change layer
            
            # three possibilities:
            # a. flipValue = rps.randomRange()
            # b. flipValue = rps.randomRange() + layerConfidence
            # c. flipValue = layerConfidence
            
            flipValue = layerConfidence
            
            layerSize = YomiData.layerConfidenceSize
            layerRange = [(0, layerSize[0])] 
            layerRange.append((layerRange[0][1], layerRange[0][1] + layerSize[1]))
            layerRange.append((layerRange[1][1], layerRange[1][1] + layerSize[2]))
            confidenceGraph = ([x for x in range(100)], layerRange)
            #confidenceGraph = ([math.log(x+0.1) for x in range(100)], layerRange)
            
            changeLayer, confidence = shouldChangeLayer(flipValue, confidenceGraph, layerLastTurn, layerToUse)

            if changeLayer == False:
                if Debug:
                    print ("Layer did not change from %i to %i.\n AI's confidence: %.2f. Missing confidence: %.2f" % 
                            (layerLastTurn, layerToUse, flipValue, confidence))
                    
                layerToUse = layerLastTurn
                
    return layerToUse
                    
def shouldUseYomi(playConfidence, yomiScore):
    # returns False if we are confident with our play
    # returns True if we are not confident with our play
    return True
                    
def decideYomiLayer(yomiData):
    # figure out what layer to use
    # 1. Get the sum of all the score
    # 2. Get the ratio for each layer
    # 3. If we are still under observation mode, don't use yomi, but keep score
    # 4. If we are, randomize what layer to choose amongst top ranking
    yomiScore = yomiData.yomiScore
        
    yomiScoreSum = 0
    for score in yomiScore:
        if score > 0:
            yomiScoreSum += score
            
    if yomiScoreSum == 0:
        chances = [1/3, 2/3, 1.0]
    else:
        chances = []
        currentCount = 1
        prevRatio = 0
        for score in yomiScore:
            if score > 0:
                ratio = score / yomiScoreSum
                chances.append(ratio)
                prevRatio = ratio
            else:
                chances.append(0)

    # make sure we don't go down the minimum layer consideration
    # if we have to modify, take from the other layers
    toModify = 0
    for chance in chances:
        if chance < yomiData.minimumLayerConsideration:
            toModify += 1
            
    if toModify and \
       toModify != len(chances):            # just a check to make sure there's a non-zero value in all the layers   
        delta = (yomiData.minimumLayerConsideration * toModify) / (len(chances) - toModify)
        if Debug:
            print ("Chances (unmodified):" + prettifyList(chances))
        for i in range(len(chances)):
            if chances[i] < yomiData.minimumLayerConsideration:
                chances[i] += yomiData.minimumLayerConsideration
            else:
                chances[i] -= delta

    rawChance = [chances[0], chances[1], chances[2]]
    
    # simplify the code by putting each ratio into a single number line
    for i in range(1, len(chances)):
        chances[i] += chances[i-1]

    if Debug: 
        print ("Yomi Score:          " + prettifyList(yomiScore))
        if toModify:
            print ("Chances (modified):  " + prettifyList(chances))            
        else:
            print ("Chances:             " + prettifyList(chances))            
        print ("Raw Chances:         " + prettifyList(rawChance))
            
    layerConfidence = 0  # how confident we are with our layer choice
    value = rps.randomRange()
    layerToUse = 0
    for i in range(len(chances)):
        if value <= chances[i]: 
            layerToUse = i
            
            total = 0
            for j in range(0, i):
                total += rawChance[j]
                
            layerConfidence = value - total
            if layerConfidence < 0: layerConfidence = 0
            break
    
    if Debug: print ("Random value was %f." % (value))

    # while in observation mode, use layer 0 except when the layer we have chosen passes the treshold.
    if YomiData.observation > 0:
        if Debug: print ("***Currently in observation mode***")
        
        if chances[layerToUse] > YomiData.layerConfidenceTresholdDuringObservationMode:
            if Debug: 
                print ("Layer Confidence Treshold reached even when under observation mode.")
                print ("Treshold: %.2f" % (YomiData.layerConfidenceTresholdDuringObservationMode))
        else:
            layerToUse = -1

    return layerToUse, layerConfidence

def getYomiChoices(prediction):    
    global yomiChoices

    # fill up yomiChoices with the moves to be played
    layer1 = (prediction + 1) % 3      # layer 1   (beats enemy's choice)
    layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
    layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
    
    yomiChoices = [layer1, layer2, layer3]

    if Debug: print ("Yomi Choices:       %i     %i     %i" % 
                     (yomiChoices[0], yomiChoices[1], yomiChoices[2]))

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
    
    # get the possible choices
    #  - decide on a move to play without predicting opponent
    #  - make a prediction
    #  - add the yomi layers to the prediction
    # decide which Yomi layer to use
    #  - (see function comments)
    # decide if we should change layer
    #  - some AI variant should change layer easily. some should change reluntanctly
    
    ourPlay = rps.random() % 3
    playConfidence = 0.0
    if shouldUseYomi(playConfidence, YomiData.yomiScore):
        yomiChoices = getYomiChoices(prediction)
        if Debug: print ("Decided to use yomi. Current play confidence is %.2f" % (playConfidence))

        layerToUse, layerConfidence = decideYomiLayer(YomiData)
        layerToUse = decideChangeLayer(YomiData, layerToUse, layerConfidence, layerLastTurn)

        layerLastTurn = layerToUse
        if layerToUse == -1:
            move = ourPlay
        else:        
            if Debug: print ("Using layer %i." % (layerToUse))

            yomiLayerUsage[layerToUse] += 1
            
            # return move based on layer
            move = yomiChoices[layerToUse]
    else:
        if Debug: print ("Decided to use personal move. Current play confidence is %.2f" % (playConfidence))
        move = ourPlay
        
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
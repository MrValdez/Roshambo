# priority:
# temporarily remove decision making for benchmarking purposes

#todo:
# make switching layers contain a cost. going higher has a higher cost. going lower has a lower cost. (this is modelling confidence)

# yomi = we are modelling what layer the opponent is susceptible to
# changing layer = we are modelling how confident we are that the opponent did not decide to change layer. In future AIs, if the opponent did something unexpected, this has a larger chance to flip.

# perlin noise instead of random?

# it seems that using yomi beats iocaine powder. using layer 0 permanently causes it lose. test to check if this is true.

import math
import rps
import yomiPredictorSelector
import RPSstrategy
Debug = True
Debug = False

# for debugging
yomiLayerScore = [0, 0, 0]        # Count how many times a yomi layer won

layerLastTurn = -1
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
        self.predictionConfidenceTreshold = 0.8  # the lowest treshold for yomi layer 1 to automatically use prediction
        
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
        self.observation = 5
        self.decayDelta = [1, 1, 1]
        self.decayDelta = [1, 0.7, 0.5]
        self.minimumLayerConsideration = 0.05
        
class YomiData:
    def __init__(self):
        personality = YomiPersonality()
        self.__dict__ = personality.__dict__.copy()

        self.yomiScore = [0, 0, 0]   
                
    def updateScore(self):
        # update score from last turn
        global yomiChoices
        global layerLastTurn
        
        currentTurn = rps.getTurn()
        if currentTurn == 0: 
            return
        
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        
        # decay the scores
        for i in range(len(self.yomiScore)):
            self.yomiScore[i] *= self.decayDelta[i]
            if self.yomiScore[i] < 0: self.yomiScore[i] = 0

        if victory:
            self.observation -= self.observationDeltaForWin
        elif tie:
            self.observation -= self.observationDeltaForTie
        else:
            self.observation -= self.observationDeltaForLost

        if self.observation:
            if victory and layerLastTurn != -1:
                self.yomiScore[layerLastTurn] += self.victoryDelta * self.layerPreference[layerLastTurn]
                
                yomiLayerScore[layerLastTurn] += 1
            else:
                if tie:
                    self.yomiScore[layerLastTurn] += self.tieDelta * self.layerPreference[layerLastTurn]
                    scoreThisTurn = self.winningDeltaForTie
                else:
                    self.yomiScore[layerLastTurn] += self.lostDelta * self.layerPreference[layerLastTurn]
                    scoreThisTurn = self.winningDeltaForLost
                
                # add score to yomi layer that would have gave us a win
                winningMove = (enemyMoveLastTurn + 1) % 3
                
                # search for the layer that contains the winning move and update it
                for i in range(len(yomiChoices)):
                    if yomiChoices[i] == winningMove:
                        self.yomiScore[i] +=  scoreThisTurn * self.layerPreference[i]
                        break

        for i in range(len(self.yomiScore)):
            if self.yomiScore[i] < 0: self.yomiScore[i] = 0

import csv

class Yomi:
    def __init__(self):
        self.YomiData = YomiData()
        self.reset()

    def reset(self):        
        self.YomiData.__init__()
        
        self.yomiChoices = [0, 0, 0]
        self.yomiLayerUsage = [0, 0, 0]        # Count how many times a yomi layer is used
    
    def _prettifyList(self, list):
        #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
        return str(["%0.3f" % i for i in list])[1:-1].replace("'", "").rjust(25)

    def _debugYomiStatUsage(self):
        if not Debug: return
        
        print ("\n\nYomi stats:  " + str(self.yomiLayerUsage))
        print ("Score stats: " + str(yomiLayerScore))
        print ("\n")
        
    def shouldChangeLayer(self, X, confidenceGraph, originLayer, targetLayer, confidenceCeiling = 0.7):
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

    def decideChangeLayer(self, layerToUse, layerConfidence, layerLastTurn):    
        # return the layer we should use. it'll either be the layer we want to use
        # or the previous layer we should stay on.

        if layerToUse == -1:
            # use our move
            return -1
            
        if layerLastTurn == layerToUse:
            # no change
            return layerToUse
            
        # see if we should change layer
        
        # three possibilities:
        # a. flipValue = rps.randomRange()
        # b. flipValue = rps.randomRange() + layerConfidence
        # c. flipValue = layerConfidence
        
        flipValue = layerConfidence
        
        layerSize = self.YomiData.layerConfidenceSize
        layerRange = [(0, layerSize[0])] 
        layerRange.append((layerRange[0][1], layerRange[0][1] + layerSize[1]))
        layerRange.append((layerRange[1][1], layerRange[1][1] + layerSize[2]))
        confidenceGraph = ([x for x in range(100)], layerRange)
        #confidenceGraph = ([math.log(x+0.1) for x in range(100)], layerRange)
        
        changeLayer, confidence = self.shouldChangeLayer(flipValue, confidenceGraph, layerLastTurn, layerToUse)

        if changeLayer == False:
            if Debug:
                print ("Layer did not change from %i to %i.\n AI's confidence: %.2f. Missing confidence: %.2f" % 
                        (layerLastTurn + 1, layerToUse + 1, flipValue, confidence))
                
            layerToUse = layerLastTurn
                    
        return layerToUse
                    
    def shouldUseYomi(self, playConfidence):
        # returns False if we are confident with our play
        # returns True if we are not confident with our play
        
        #todo: check sum here
            
        return True
                        
    def decideYomiLayer(self, predictionConfidence):
        # figure out what layer to use
        # 1. Get the sum of all the score
        # 1b. Add the confidence we have on prediction
        # 2. Normalize the layers to 1.0
        # 3a. If we are still under observation mode, don't use yomi, but keep score
        # 3b. If we are not under observation mode, choose a layer
        
        if predictionConfidence >= self.YomiData.predictionConfidenceTreshold:
            if Debug: 
                print ("High confidence of predicting opponent at %.2f. Treshold %.2f" % (predictionConfidence, self.YomiData.predictionConfidenceTreshold))
            return 0, predictionConfidence

        yomiScore = [score for score in self.YomiData.yomiScore]

        # add prediction confidence to layer chances
        if Debug: 
            print ("Layer 0's confidence: %.2f. Prediction confidence: %.2f" % (yomiScore[0], predictionConfidence))

        predictionConfidenceDelta = max(yomiScore[0], predictionConfidence)
        yomiScore[0] = predictionConfidenceDelta
        
        # normalize everything to 1        
        total = sum([score for score in yomiScore if score > 0])
        
        chances = []
        if total == 0:
            chances = [0, 0, 0]
        else:
            normal = 1 / total
            for score in yomiScore:
                if score > 0:
                    ratio = score * normal
                    chances.append(ratio)
                else:
                    chances.append(0)

        # make sure we don't go down the minimum layer consideration
        # if we have to modify, take from the other layers
        minimumLayerConsideration = self.YomiData.minimumLayerConsideration
        numberOfBelowLayerConsideration = 0
        for chance in chances:
            if chance < minimumLayerConsideration:
                numberOfBelowLayerConsideration += 1
                
        if numberOfBelowLayerConsideration:    # check to make sure there's a non-zero value in all the layers   
            aboveMinimumLayerConsideration = len(chances) - numberOfBelowLayerConsideration
            if aboveMinimumLayerConsideration == 0: aboveMinimumLayerConsideration = 1
            
            delta = (minimumLayerConsideration * numberOfBelowLayerConsideration) / aboveMinimumLayerConsideration
            if Debug: print ("Chances (unmodified):" + self._prettifyList(chances))
            
            for i in range(len(chances)):
                if chances[i] < minimumLayerConsideration:
                    chances[i] += minimumLayerConsideration
                else:
                    chances[i] -= delta

        rawChance = [chances[0], chances[1], chances[2]]
        
        # simplify the code by putting each ratio into a single number line
        for i in range(1, len(chances)):
            chances[i] += chances[i - 1]

        if Debug: 
            prettifyList = self._prettifyList
            print ("Yomi Score:          " + prettifyList(yomiScore))
            if numberOfBelowLayerConsideration:
                print ("Chances (modified):  " + prettifyList(chances))            
            else:
                print ("Chances:             " + prettifyList(chances))            
            print ("Raw Chances:         " + prettifyList(rawChance))
                
        layerConfidence = 0  # how confident we are with our layer choice
        value = rps.randomRange()
        if Debug: print ("Random value was %f." % (value))
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
        else:
            if Debug: print ("No confidence in yomi")
            return -1, layerConfidence
            
        # while in observation mode, use layer -1 except when the layer we have chosen passes the treshold.
        if self.YomiData.observation > 0:
            if Debug: print ("***Currently in observation mode***")
            
            if chances[layerToUse] > self.YomiData.layerConfidenceTresholdDuringObservationMode:
                if Debug: 
                    print ("Layer Confidence Treshold reached even when under observation mode.")
                    print ("Treshold: %.2f" % (self.YomiData.layerConfidenceTresholdDuringObservationMode))
            else:
                layerToUse = -1

        return layerToUse, layerConfidence

    def getYomiChoices(self, move):    
        global yomiChoices
        
        # fill up yomiChoices with the moves to be played
        layer1 = (move   + 1) % 3          # layer 1   (beats enemy's choice)
        layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
        layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
        
        yomiChoices = [layer1, layer2, layer3]

        if Debug: print ("Yomi Choices:                  %i      %i      %i" % 
                         (yomiChoices[0], yomiChoices[1], yomiChoices[2]))

        return yomiChoices

    def play(self, ownPlay, prediction):
        global layerLastTurn
        
        self.YomiData.updateScore()
            
        self._debugYomiStatUsage()
        
        # get the possible choices
        #  - decide on a move to play without predicting opponent
        #  - make a prediction
        #  - add the yomi layers to the prediction
        # decide which Yomi layer to use
        #  - (see function comments)
        #  - if we are not very confident with our Yomi, we stick to our own play
        # decide if we should change layer
        #  - some AI variant should change layer easily. some should change reluntanctly
        
        ownPlayConfidence = ownPlay[1]
        if self.shouldUseYomi(ownPlayConfidence):        
            yomiChoices = self.getYomiChoices(prediction[0])
            if Debug: print ("Decided to use yomi. Current play confidence is %.2f" % (playConfidence))

            predictionConfidence = prediction[1]
            layerToUse, layerConfidence = self.decideYomiLayer(predictionConfidence)
            layerToUse = self.decideChangeLayer(layerToUse, layerConfidence, layerLastTurn)
            
            if layerToUse == -1:
                if Debug: print ("Using our play (layer -1).")
                move = ownPlay[0]
                predictorSelector.LastPredictor = None   # todo: move to predictorSelector
            else:        
                if Debug: print ("Using layer %i." % (layerToUse + 1))

                self.yomiLayerUsage[layerToUse] += 1
                
                # return move based on layer
                move = yomiChoices[layerToUse]
                
            layerLastTurn = layerToUse
        else:
            if Debug: print ("Decided to use personal move. Current play confidence is %.2f" % (playConfidence))
            move = ownPlay[0]
            predictorSelector.LastPredictor = None   # todo: move to predictorSelector
            
        return move
    
yomi = Yomi()
strategy = RPSstrategy.RPSstrategy()
predictorSelector = yomiPredictorSelector.PredictorSelector()

def play(a):
    currentTurn = rps.getTurn() 
    
    global Debug
    if Debug:
        if currentTurn == 0: 
            print("\n\n")
        else:             
            if not yomi.YomiData.observation > 0:    # skip to the point when we are no longer observing
                input()
            else:
                print()

    if currentTurn == 999:
        yomi._debugYomiStatUsage()

        # This code is for jumping into a specific opponent for debugging
        global currentOpponent
        currentOpponent += 1
        if currentOpponent == 2:
            #Debug = True
            pass
            
    if currentTurn == 0:
        strategy.reset()
        predictorSelector.reset()
        yomi.reset()
    
    strategy.update()
    ownPlay = strategy.play()
        
    predictorSelector.update()
    prediction = predictorSelector.getHighestRank(a)
    
    decision = yomi.play(ownPlay, prediction)
    
    return decision
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    global Debug
    return Debug
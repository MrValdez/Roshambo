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
currentOpponent = 0               # This code is for jumping into a specific opponent for debugging

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

import csv

class Yomi:
    def __init__(self):
        self.Personality = YomiPersonality()
        self.reset()

    def reset(self):
        self.Personality.__init__()
        
        self.yomiChoices = [0, 0, 0]
        self.yomiLayerUsage = [0, 0, 0]        # Count how many times a yomi layer is used
        self.yomiScore = [0, 0, 0]
        self.layerLastTurn = -1
    
    def _prettifyList(self, list):
        #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
        return str(["%0.3f" % i for i in list])[1:-1].replace("'", "").rjust(25)

    def _debugYomiStatUsage(self):
        if not Debug: return
        
        print ("\n\nYomi stats:  " + str(self.yomiLayerUsage))
        print ("Score stats: " + str(yomiLayerScore))
        print ("\n")        
                
    def updateScore(self):
        # update score from last turn        
        currentTurn = rps.getTurn()
        if currentTurn == 0: 
            return
        
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        
        personality = self.Personality
        
        for i, _ in enumerate(self.yomiScore):
            self.yomiScore[i] *= personality.decayDelta[i]
            if self.yomiScore[i] < 0: self.yomiScore[i] = 0
        
        if victory:
            self.Personality.observation -= personality.observationDeltaForWin
        elif tie:
            self.Personality.observation -= personality.observationDeltaForTie
        else:
            self.Personality.observation -= personality.observationDeltaForLost

        if self.layerLastTurn != -1:
            layerLastTurn = self.layerLastTurn
            if victory:
                self.yomiScore[layerLastTurn] += personality.victoryDelta * personality.layerPreference[layerLastTurn]
                
                global yomiLayerScore
                yomiLayerScore[layerLastTurn] += 1
            else:
                if tie:
                    self.yomiScore[layerLastTurn] += personality.tieDelta * personality.layerPreference[layerLastTurn]
                    scoreThisTurn = personality.winningDeltaForTie
                else:
                    self.yomiScore[layerLastTurn] += personality.lostDelta * personality.layerPreference[layerLastTurn]
                    scoreThisTurn = personality.winningDeltaForLost
                
                # add score to yomi layer that would have gave us a win
                winningMove = (enemyMoveLastTurn + 1) % 3
                
                # search for the layer that contains the winning move and update it
                for i in range(len(self.yomiChoices)):
                    if self.yomiChoices[i] == winningMove:
                        self.yomiScore[i] +=  scoreThisTurn * personality.layerPreference[i]
                        break

        for i, _ in enumerate(self.yomiScore):
            if self.yomiScore[i] < 0: 
                self.yomiScore[i] = 0

    def shouldUseYomi(self, playConfidence):
        # returns False if we are confident with our play
        # returns True if we are not confident with our play
        
        #todo: check sum here
            
        return True
                        
    def getYomiChoices(self, move):    
        # fill up yomiChoices with the moves to be played
        layer1 = (move   + 1) % 3          # layer 1   (beats enemy's choice)
        layer2 = (layer1 + 2) % 3          # layer 2   (beats enemy's layer 1)
        layer3 = (layer2 + 2) % 3          # layer 3   (beats enemy's layer 2)
        
        yomiChoices = [layer1, layer2, layer3]
        self.yomiChoices = yomiChoices

        if Debug: print ("Yomi Choices:                  %i      %i      %i" % (yomiChoices[0], yomiChoices[1], yomiChoices[2]))

        return yomiChoices

    def decideYomiLayer(self, predictionConfidence):
        return 0, 1.0

    def play(self, predictorSelector, ownPlay, ownPlayConfidence, prediction, predictionConfidence): 
        self.updateScore()            
        self._debugYomiStatUsage()

        # decide if we need to use the prediction
        #  - if true, add the yomi layers to the prediction
        #  - else, use own play
        # decide which Yomi layer to use
        #  - (see function comments)
        #  - if we are not very confident with our Yomi, we stick to our own play
        # decide if we should change layer
        #  - some AI variant should change layer easily. some should change reluntanctly
        
        yomiChoices = self.getYomiChoices(prediction)

        layerToUse, layerConfidence = self.decideYomiLayer(predictionConfidence)
        predictorSelector.LastYomiLayer = layerToUse
                
        if layerToUse == -1:
            if Debug: print ("Using our play (layer 0).")
            move = ownPlay
            predictorSelector.LastPredictor = None
        else:        
            if Debug: print ("Using layer %i." % (layerToUse + 1))

            self.yomiLayerUsage[layerToUse] += 1
            
            # return move based on layer
            move = yomiChoices[layerToUse]
            
        self.layerLastTurn = layerToUse
        return move

def startDebugTurn():
    currentTurn = rps.getTurn() 

    global Debug   
    if Debug: 
        if not yomi.Personality.observation > 0:    # skip to the point when we are no longer observing
            input()

    if currentTurn == 999:
        yomi._debugYomiStatUsage()

        # This code is for jumping into a specific opponent for debugging
        global currentOpponent
        currentOpponent += 1
        if currentOpponent == 2:
            #Debug = True
            pass
    
yomi = Yomi()
strategy = RPSstrategy.RPSstrategy()
predictorSelector = yomiPredictorSelector.PredictorSelector()

#to test specific prediction, uncomment:
import PatternPredictor
import BeatFrequentPick
#import MBFP
Predictor = None

def play(a):
    #to test specific prediction, uncomment:
    #global Predictor
    #if Predictor == None:
    #    Predictor = PatternPredictor.PatternPredictor(a)
    #    Predictor = BeatFrequentPick.MBFP(a)
    #Predictor.update()
    #predict = Predictor.play()[0]
    #return (predict + 1) % 3
        
    startDebugTurn()
    
    if rps.getTurn() == 0:
        strategy.reset()
        predictorSelector.reset()
        yomi.reset()
    
    strategy.update()
    ownPlay, ownPlayConfidence = strategy.play()
    
    predictorSelector.update()
    prediction, predictionConfidence = predictorSelector.getHighestRank()

    #to test prediction ranking, uncomment:
    #return (prediction[0] + 1) % 3
    
    decision = yomi.play(predictorSelector, ownPlay, ownPlayConfidence, prediction, predictionConfidence)
    return decision
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    global Debug
    return Debug
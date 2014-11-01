#todo:
# make switching layers contain a cost. going higher has a higher cost. going lower has a lower cost. (this is modelling confidence)

# yomi = we are modelling what layer the opponent is susceptible to
# changing layer = we are modelling how confident we are that the opponent did not decide to change layer. In future AIs, if the opponent did something unexpected, this has a larger chance to flip.

# perlin noise instead of random?

import math
import rps
import yomiPredictorSelector
import RPSstrategy

Debug = True
Debug = False

# for debugging
currentOpponent = 0               # This code is for jumping into a specific opponent for debugging

import csv

class Yomi:
    def __init__(self):
        self.reset()

    def reset(self):        
        self.yomiChoices = [0, 0, 0]           # Holds the choices in each yomi layer.
        self.yomiScore = [0, 0, 0]             # The victory points each score received. Seperate from yomiLayerUsage because points have different values.
        self.yomiLayerUsage = [0, 0, 0]        # Count how many times a yomi layer is used
        self.yomiLayerWins = [0, 0, 0]         # Count how many times a yomi layer won
        self.layerLastTurn = -1
        self.ownStrategyUsage = 0               # count how many times we used our own strategy
        
        self.startingYomiScore = -10
        startingYomiScore = self.startingYomiScore 
        for i, _ in enumerate(self.yomiScore):
            self.yomiScore[i] = startingYomiScore
    
    def _prettifyList(self, list):
        #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
        return str(["%0.3f" % i for i in list])[1:-1].replace("'", "").rjust(25)

    def _debugYomiStatUsage(self):
        if not Debug: return
        
        print ("\n\nYomi usage stats:  " + self._prettifyList(self.yomiLayerUsage))
        print ("Yomi Score stats:  " + self._prettifyList(self.yomiScore))
        print ("Yomi wins stats:   " + self._prettifyList(self.yomiLayerWins))
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
        
        victoryPoints = 2
        tiePoints = 1
        lostPoints = -2

        layerLastTurn = self.layerLastTurn
        
        # update layer we used last turn
        if layerLastTurn != -1:
            self.yomiLayerUsage[layerLastTurn] += 1
            
            if victory:
                self.yomiScore[layerLastTurn] += victoryPoints
                self.yomiLayerWins[layerLastTurn] += 1
            else:
                if tie:
                    self.yomiScore[layerLastTurn] += tiePoints
                else:
                    self.yomiScore[layerLastTurn] += lostPoints

        # update other layers
        for i, _ in enumerate(self.yomiScore):
            if i != layerLastTurn:
                myMoveLastTurn = self.yomiChoices[i]
                tie = (myMoveLastTurn == enemyMoveLastTurn)
                lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
                
                if lost:
                    if self.yomiScore[i] > 0:
                        self.yomiScore[i] -= 1
                elif tie:
                    self.yomiScore[i] += 1
                
        # add score to yomi layer that would have gave us a win
        # todo: is it better to remove this as to stop double-guessing?
        winningMove = (enemyMoveLastTurn + 1) % 3
        
        # search for the layer that contains the winning move and update it
        try:
            i = self.yomiChoices.index(winningMove)
        except ValueError:
            pass
        else:
            self.yomiScore[i] += victoryPoints
            pass
                    
        for i, _ in enumerate(self.yomiScore):
            if self.yomiScore[i] < self.startingYomiScore: 
                self.yomiScore[i] = self.startingYomiScore 
            #if self.yomiScore[i] < -3: 
            #    self.yomiScore[i] = -3
            #if self.yomiScore[i] < 0: 
            #    self.yomiScore[i] += 2
            self.yomiScore[i] += 1
            pass

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

        if Debug: print ("Yomi Choices:          %i      %i      %i" % (yomiChoices[0], yomiChoices[1], yomiChoices[2]))

        return yomiChoices

    def decideYomiLayer(self, predictionConfidence):
        maxScore = max(self.yomiScore)
        if maxScore < 0:
            #print("using layer 0")
            self.ownStrategyUsage += 1
            return -1, 1.0
            
        yomiLayer = self.yomiScore.index(maxScore)
        return yomiLayer, 1.0

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
        if currentTurn:    # skip to the point when we are no longer observing
        #if currentTurn and not yomi.Personality.observation > 0:    # skip to the point when we are no longer observing
            input()
            print("**next turn**")

    if currentTurn == 999:
        yomi._debugYomiStatUsage()
        #print (yomi.ownStrategyUsage)

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
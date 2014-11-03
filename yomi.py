#todo:
# make switching layers contain a cost. going higher has a higher cost. going lower has a lower cost. (this is modelling confidence)

# yomi = we are modelling what layer the opponent is susceptible to
# changing layer = we are modelling how confident we are that the opponent did not decide to change layer. In future AIs, if the opponent did something unexpected, this has a larger chance to flip.

# perlin noise instead of random?

import math
import rps
import yomiPredictorSelector
import RPSstrategy

import socket
from debuggerOpcodes import *

class VisualDebugger:
    def connect(self):
        try:
            port = 42
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("localhost", port))
            
            self.conn = s
           
            self.conn.send(OPCODE_NewTournament)
            self.connected = True
        except:
            self.connected = False
        
    def NextAI(self, name):
        if not self.connected: return
        
        self.conn.send(OPCODE_NextAI)    
        size = len(name)
        self.conn.send(bytes([size]))        # we send the length of the string first. This is unnecessary in TCP/IP but it is for UDP.
        self.conn.send(bytes(name, "utf-8"))
        
    def SendLayer(self, layer):
        if not self.connected: return        
        currentTurn = rps.getTurn()
        if currentTurn == 0: 
            name = rps.enemyName()
            self.NextAI(name)

        if layer == -1:
            self.conn.send(OPCODE_ActivateLayer0)
        elif layer == 0:
            self.conn.send(OPCODE_ActivateLayer1)
        elif layer == 1:
            self.conn.send(OPCODE_ActivateLayer2)
        elif layer == 2:
            self.conn.send(OPCODE_ActivateLayer3)

    def close(self):
        if not self.connected: return
        conn.close()
    

Debug = True
Debug = False


# for debugging
currentOpponent = 0               # This code is for jumping into a specific opponent for debugging

import csv

class Yomi:
    def __init__(self):
        self.VisualDebugger = VisualDebugger()
        self.VisualDebugger.connect()
        self.reset()

    def reset(self):        
        self.yomiChoices = [0, 0, 0]           # Holds the choices in each yomi layer.
        self.yomiLayerWins = [0, 0, 0]         # Count how many times a yomi layer won
        self.yomiLayerLosts = [0, 0, 0]        # Count how many times a yomi layer losts
        self.layerLastTurn = -1        
    
    def _prettifyList(self, list):
        #return "[%.2f %.2f %.2f %.2f]" % (list[0], list[1], list[2], list[3])
        return str(["%0.3f" % i for i in list])[1:-1].replace("'", "").rjust(25)

    def _debugYomiStatUsage(self):
        if not Debug: return
        
        print ("\n\nYomi wins stats:   " + self._prettifyList(self.yomiLayerWins))
        print ("Yomi losts stats:  " + self._prettifyList(self.yomiLayerLosts))
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
        
        layerLastTurn = self.layerLastTurn
        
        # update layer we used last turn
        for i, _ in enumerate(self.yomiLayerWins):
            myMoveLastTurn = self.yomiChoices[i]
            victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
            tie = (myMoveLastTurn == enemyMoveLastTurn)
            lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)               
            
            if victory:
                self.yomiLayerWins[i] += 1
            elif tie:
                self.yomiLayerWins[i] += 1
                self.yomiLayerLosts[i] += 1
            else:
                self.yomiLayerLosts[i] += 1                                            
                    
        return
        
        
                
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

    def decideYomiLayer(self, predictionConfidence, ownPlayConfidence):    
        if ownPlayConfidence > predictionConfidence:
            return -1, ownPlayConfidence

        if max(self.yomiLayerWins) <= ownPlayConfidence:
            return -1, ownPlayConfidence               

        confidences = []
        for i in [0, 1, 2]:
            if self.yomiLayerWins[i] > 0:
                yomiConfidence = (self.yomiLayerWins[i] - self.yomiLayerLosts[i]) / self.yomiLayerWins[i]
            else:
                yomiConfidence = 0
            
            if i == 0:
                yomiConfidence = (yomiConfidence * 0.5) + (predictionConfidence * 0.5)
            elif i == 1:
                yomiConfidence = (yomiConfidence * 0.25) + (predictionConfidence * 0.75)
                yomiConfidence = 0
            elif i == 2:
                yomiConfidence = (yomiConfidence * 0.15) + (predictionConfidence * 0.85)
                yomiConfidence = 0
                
            confidences.append(yomiConfidence)
        
        confidence = max(confidences)
        yomiLayer = confidences.index(confidence)

        if confidence < ownPlayConfidence:
            return -1, ownPlayConfidence                   
        
        return yomiLayer, confidence

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

        layerToUse, layerConfidence = self.decideYomiLayer(predictionConfidence, ownPlayConfidence)
        predictorSelector.LastYomiLayer = layerToUse
        if layerToUse == -1:
            if Debug: print ("Using our play (layer 0).")
            #print ("Using our play (layer 0).")
            move = ownPlay
            predictorSelector.LastPredictor = None
        else:        
            if Debug: print ("Using layer %i." % (layerToUse + 1))
            
            # return move based on layer
            move = yomiChoices[layerToUse]
            
        self.layerLastTurn = layerToUse

        self.VisualDebugger.SendLayer(layerToUse)
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
    
import time    
startTime = time.time()
    
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
    global Predictor
#    if Predictor == None:
#        Predictor = PatternPredictor.PatternPredictor(a)
#        Predictor = BeatFrequentPick.MBFP(a)
#    Predictor.update()
#    predict = Predictor.play()[0]
#    return (predict + 1) % 3
        
    startDebugTurn()
    
    if rps.getTurn() == 0:
        strategy.reset()
        predictorSelector.reset()
        yomi.reset()
    
    strategy.update()
    ownPlay, ownPlayConfidence = strategy.play()
    
    predictorSelector.update()
    prediction, predictionConfidence = predictorSelector.getPrediction()
    
    decision = yomi.play(predictorSelector, ownPlay, ownPlayConfidence, prediction, predictionConfidence)
    
    #to test prediction ranking, uncomment:
    #decision = (prediction + 1) % 3
      
    if rps.getTurn() == 999:
        global startTime
        endTime = time.time()
        #print ("\nTotal time elapsed:", endTime - startTime)
        startTime = endTime
    return decision
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    global Debug
    return Debug
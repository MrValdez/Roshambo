#todo:
# make switching layers contain a cost. going higher has a higher cost. going lower has a lower cost. (this is modelling confidence)

# yomi = we are modelling what layer the opponent is susceptible to
# changing layer = we are modelling how confident we are that the opponent did not decide to change layer. In future AIs, if the opponent did something unexpected, this has a larger chance to flip.

# perlin noise instead of random?

import sys      # pykov and scipy depedencies
#sys.path.append(r"\Windows\System32\python34.zip")
sys.path.append(r"\Python34")
sys.path.append(r"\Python34\lib")
sys.path.append(r"\Python34\lib\site-packages")
sys.path.append(r"\Python34\dlls")

import pykov
from pprint import pprint

import math
import rps
import yomiPredictorSelector
import RPSstrategy

Debug = True
Debug = False

# for debugging
currentOpponent = 0               # This code is for jumping into a specific opponent for debugging

import csv

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

        print("Disconnecting from debugger...")
        
        # tell the server we are disconnecting. Wait for the server to say ok.
        self.conn.send(OPCODE_Exit)
        data = None
        while data != OPCODE_Exit:
            data = self.conn.recv(1)
        
        self.conn.close()
        self.connected = False

    def __del__(self):
        print("deleting")
        self.close()

class Yomi:
    def __init__(self):
        self.VisualDebugger = VisualDebugger()
        self.VisualDebugger.connect()
        self.reset()

    def reset(self):        
        self.yomiChoices = [0, 0, 0]           # Holds the choices in each yomi layer.
        self.yomiLayerWins = [0, 0, 0]         # Count how many times a yomi layer won
        self.yomiLayerLosts = [0, 0, 0]        # Count how many times a yomi layer lost
        
        #towrite: yomilayerwins and yomilayerlosts are within one shift with each other. Makes sense but write as trivia?
        
        self.yomiLayerTies = [0, 0, 0]        # Count how many times a yomi layer tied
        self.layerLastTurn = -1        
        
        self.currentYomiModel = ""
        self.yomiModels = [ [], [], [] ]
        
        self.yomiHistory = ""
        self.yomiHistorySize = 50
        self.yomiHistoryWins = ""
        self.yomiHistoryWinsSize = 5           # target for DNA
        
        self.enemyConfidence = 0
        self.totalWins = 0
        self.totalLosts = 0
    
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

        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        layerToWin = -1
        # update yomi layers' scores
        for i, _ in enumerate(self.yomiLayerWins):
            myMoveLastTurn = self.yomiChoices[i]
            victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
            tie = (myMoveLastTurn == enemyMoveLastTurn)
            lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)            
            
            if victory:
                self.yomiLayerWins[i] += 1
                layerToWin = i
                self.yomiHistoryWins += str(i)
                self.yomiHistoryWins = self.yomiHistoryWins[-self.yomiHistoryWinsSize:]
            elif tie:
                self.yomiLayerTies[i] += 1
            else:
                self.yomiLayerLosts[i] += 1

        myMoveLastTurn = rps.myHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)            
        if victory:
            self.totalWins += 1
        elif lost:
            self.totalLosts += 1


        layerLastTurn = self.layerLastTurn
        #if layerLastTurn != 0: print(layerLastTurn)
        if layerLastTurn == -1:
            return
                    
        self.currentYomiModel += str(layerLastTurn)
        if lost or tie:
            if len(self.currentYomiModel):
                failedModel = self.currentYomiModel
                #print (failedModel)
                #print(self.yomiModels)
                if failedModel in self.yomiModels[layerLastTurn]:
                    print("fail")
                    self.yomiModels[layerLastTurn].remove(failedModel)
                self.yomiModels[layerToWin].append(self.currentYomiModel)
            self.currentYomiModel = ""
        
        self.yomiHistory += str(layerLastTurn)
        self.yomiHistory = self.yomiHistory[-self.yomiHistorySize:]
                                        
        if victory:
            self.enemyConfidence -= rps.randomRange() * 0.1
        if lost or tie:
            self.enemyConfidence += rps.randomRange() * 0.1
            
        if self.enemyConfidence < 0: self.enemyConfidence = 0
        if self.enemyConfidence > 1: self.enemyConfidence = 1
        

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
                
        if ownPlayConfidence == predictionConfidence:
            # flip a coin
            if rps.randomRange() <= 0.5:
                return -1, ownPlayConfidence
       
#######
# monte carlo
# (reversing player's yomi layer) http://nbviewer.ipython.org/github/fonnesbeck/Bios366/blob/master/notebooks/Section4_2-MCMC.ipynb
# technical info on markov chain: http://www.biochem-caflisch.uzh.ch/rscalco/pykov/getting_started.html
#                                 https://github.com/riccardoscalco/Pykov       
        layerLastTurn = self.layerLastTurn
        if layerLastTurn == -1: start = "A"
        if layerLastTurn == 0:  start = "A"
        if layerLastTurn == 1:  start = "B"
        if layerLastTurn == 2:  start = "C"

        # Benford's law
        # 1 	30.1% 	
        # 2 	17.6% 	
        # 3 	12.5% 	
        
        if predictionConfidence == 1:
            stayLayer1Confidence = 1
            if start == "A":
                return 0, predictionConfidence
        else:
            stayLayer1Confidence = predictionConfidence
  
        layer2Confidence = 1 - stayLayer1Confidence
        layer3Confidence = layer2Confidence #* 0.176
        
        # probability in staying in the same layer
        stayLayer2Confidence = layer2Confidence #* (1 - 0.301)
        stayLayer3Confidence = layer3Confidence #* (1 - 0.125)
        
        # probability in moving to a lower layer
        backLayer1Confidence = 1.0 - stayLayer2Confidence
        backLayer2Confidence = 1.0 - stayLayer3Confidence
                
        # add yomi win stats
        #yomiLayerWins = self.yomiLayerWins
        
        yomiHistory = self.yomiHistoryWins
        yomiLayerWins = [yomiHistory.count("0"), yomiHistory.count("1"), yomiHistory.count("2")]                         
        #print(yomiHistory, yomiLayerWins)
        #input()
        
        total = sum(yomiLayerWins)
        if 1 and total:
            influence1 = yomiLayerWins[0] / total
            influence2 = yomiLayerWins[1] / total
            influence3 = yomiLayerWins[2] / total

            if 0:
                delta1 = .5         #dna
                delta2 = .5
                
                delta1 = .9         #dna
                delta2 = .1
                # layer A
                stayLayer1Confidence = (stayLayer1Confidence * delta1) + (influence1 * delta2)
                backLayer1Confidence = (backLayer1Confidence * delta1) + (influence1 * delta2)
                # layer B
                layer2Confidence     = (layer2Confidence     * delta1) + (influence2 * delta2)
                stayLayer2Confidence = (stayLayer2Confidence * delta1) + (influence2 * delta2)
                backLayer2Confidence = (backLayer2Confidence * delta1) + (influence2 * delta2)
                # layer C
                layer3Confidence     = (layer3Confidence     * delta1) + (influence3 * delta2)
                stayLayer3Confidence = (stayLayer3Confidence * delta1) + (influence3 * delta2) 
            else:        
                # layer A
                stayLayer1Confidence += influence1
                backLayer1Confidence += influence1
                # layer B
                layer2Confidence     += influence2
                stayLayer2Confidence += influence2
                backLayer2Confidence += influence2
                # layer C
                layer3Confidence     += influence3
                stayLayer3Confidence += influence3            

        transitionAA = stayLayer1Confidence
        transitionAB = layer2Confidence
        
        transitionBA = backLayer1Confidence
        transitionBB = stayLayer2Confidence
        transitionBC = layer3Confidence
        
        transitionCA = stayLayer1Confidence
        transitionCB = backLayer2Confidence
        transitionCC = stayLayer3Confidence
        
        if 0:
            normal = (transitionAA + transitionAB)
            if normal < 1: normal = 1.0
            transitionAA /= normal
            transitionAB /= normal

            normal = (transitionBA + transitionBB + transitionBC)
            if normal < 1: normal = 1.0
            transitionBA /= normal
            transitionBB /= normal
            transitionBC /= normal
            
            normal = (transitionCA + transitionCB + transitionCC)
            if normal < 1: normal = 1.0
            transitionCA /= normal
            transitionCB /= normal
            transitionCC /= normal
            
        from collections import OrderedDict
        yomi = OrderedDict((
                (("A", "A"), transitionAA), (("A", "B"), transitionAB),
                (("B", "A"), transitionBA), (("B", "B"), transitionBB), (("B", "C"), transitionBC),
                (("C", "A"), transitionCA), (("C", "B"), transitionCB), (("C", "C"), transitionCC)))
        p = pykov.Chain(yomi)
                    
        result = p.move(start, rps.randomRange)
        
        if 0:
            currentTurn = rps.getTurn()
            print ("Current Turn: ", currentTurn)
            print ("Confidence  : ", predictionConfidence)
            pprint (p)
            print ("Last Turn   : ", start)
            print ("Result      : ",result)
            input()
        
        if result == "A":   return 0, predictionConfidence
        if result == "B":   return 1, layer2Confidence
        if result == "C":   return 2, layer3Confidence
        
        return -1, 0
#######        


#######
#        random = rps.randomRange()

#        if random < predictionConfidence:
#            return 0, predictionConfidence      # layer 1

#        return 1, predictionConfidence          # layer 2
#######
                    
#######
        #return rps.biased_roshambo(0.35,0.25), predictionConfidence     # weak
#######

#######        
        # Benford's law
        # 1 	30.1% 	
        # 2 	17.6% 	
        # 3 	12.5% 	
        # 4 	9.7% 	
        # 5 	7.9% 	
        # 6 	6.7% 	
        # 7 	5.8% 	
        # 8 	5.1% 	
        # 9 	4.6% 	

        ratio = 1.0 / 3
        confidences = [ratio] * 3
        for i in [0, 1, 2]:
            yomiConfidence = (self.yomiLayerWins[i] - (self.yomiLayerLosts[i] + self.yomiLayerTies[i])) / currentTurn
            
            if i == 0:
                confidences[i] = (predictionConfidence * 0.67) + (yomiConfidence * 0.33)
            else:
                confidences[i] = (confidences[i - 1] * 0.67) + (yomiConfidence * 0.33)
        
        #print(confidences, sum(confidences))

        random = rps.randomRange()
        if random < confidences[0]:
            return 0, predictionConfidence      # layer 1
        random -= confidences[0]
        
        if random < confidences[1]:
            return 1, predictionConfidence          # layer 2
        random -= confidences[1]
        
        if random < confidences[2]:
            return 2, predictionConfidence          # layer 3
        
        return -1, ownPlayConfidence
#######

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
    
def shutdown():
    yomi.VisualDebugger.close()
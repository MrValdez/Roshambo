import rps
from rps import biased_roshambo

Debug = True
Debug = False

class MBFP:
    def __init__(self, targetPredictionSize):
        self.targetPredictionSize = int(targetPredictionSize)
        self.reset()
        
    def reset(self):
        self.statR, self.statP, self.statS = 0, 0, 0
        self.remainingPredictionSize = self.targetPredictionSize
        self.probR = 1 / 3.0
        self.probP = 1 / 3.0
        self.predictionR = self.probR * self.targetPredictionSize
        self.predictionP = self.probP * self.targetPredictionSize
        self.updateTurn = 0

        if Debug:
            print("\n\nInitial data (Target Prediction Size %i):\n" % (self.targetPredictionSize))
            print("statR, statP:                         %i    %i" % (self.statR, self.statP));
            print("predictionR, predictionP:             %.2f %.2f" % (self.predictionR, self.predictionP));
            print("currentTurn, remainingPredictionSize: %i    %i" % (rps.getTurn(), self.remainingPredictionSize))
            print("Done init()\n")

    def update(self):
        currentTurn = rps.getTurn()
        if (currentTurn == 0):
            self.reset()
        
        oppMove = rps.enemyHistory(currentTurn)
        
        if (oppMove == 0):
            self.statR += 1
        if (oppMove == 1):
            self.statP += 1
        if (oppMove == 2):
            self.statS += 1
    
    def calculateProbThisTurn(self):
        thisTurnProbR = float((self.predictionR - self.statR) / float(self.remainingPredictionSize))
        thisTurnProbP = float((self.predictionP - self.statP) / float(self.remainingPredictionSize))
        
        return thisTurnProbR, thisTurnProbP

    def recomputeFutureProb(self, currentTurn, targetPredictionSize):
        self.probR = self.statR / float (currentTurn)
        self.probP = self.statP / float (currentTurn)
        
        self.predictionR = float(self.probR * (currentTurn + targetPredictionSize))
        self.predictionP = float(self.probP * (currentTurn + targetPredictionSize))
        
        self.remainingPredictionSize = targetPredictionSize

    def predict(self, targetPredictionSize):
        currentTurn = rps.getTurn()
        if (currentTurn == 0):
            return biased_roshambo (1 / 3.0, 1 / 3.0), 1 / 3.0

        turnsUpdated = currentTurn - self.updateTurn     # how many turns to predict
        self.updateTurn = currentTurn
        
        move = 0
        confidence = 0
        while turnsUpdated:
            turnsUpdated -= 1
            
            if (self.remainingPredictionSize <= 0):
                if Debug:
                    print ("***********************")
                    print ("Recomputing remainingPredictionSize")
                    print ("***********************")
                    
                self.recomputeFutureProb(currentTurn, targetPredictionSize)
                
            thisTurnProbR, thisTurnProbP = self.calculateProbThisTurn()

            if Debug:
                print("currentTurn, remainingPredictionSize: %i    %i" % (currentTurn, self.remainingPredictionSize))
                print("statR, statP:                         %i    %i" % (self.statR, self.statP));
                print("probR, probP:                         %.2f %.2f" % (self.probR, self.probP));
                print("predictionR, predictionP:             %.2f %.2f" % (self.predictionR, self.predictionP));
                print("thisTurnProbR, thisTurnProbP:         %.2f %.2f" % (thisTurnProbR, thisTurnProbP))
                debugRecomputation = False
                
            if (thisTurnProbR < 0 or thisTurnProbP < 0 or thisTurnProbR + thisTurnProbP > 1.0):
                if Debug:
                    debugRecomputation = True
                    print ("***********************")
                    print ("Recomputing because of", thisTurnProbR <= 0, thisTurnProbP <= 0, thisTurnProbR + thisTurnProbP >= 1.0)
                    print ("***********************")
                    
                self.recomputeFutureProb(currentTurn, targetPredictionSize)
                thisTurnProbR, thisTurnProbP = self.calculateProbThisTurn()

            # These two checks will never be True as proven by studying the algorithm. 
            # But in the interest of keeping this program bug free (and for the sanity of the coder), they are added
            thisTurnProbR = 0 if thisTurnProbR < 0 else thisTurnProbR
            thisTurnProbP = 0 if thisTurnProbP < 0 else thisTurnProbP
            
            if Debug and debugRecomputation:
                print("predictionR, predictionP:             %.2f %.2f" % (self.predictionR, self.predictionP));
                print("thisTurnProbR, thisTurnProbP:         %.2f %.2f\n" % (thisTurnProbR, thisTurnProbP))
            
                
            self.remainingPredictionSize -= 1
            move = biased_roshambo (thisTurnProbR, thisTurnProbP)
            
            # get our confidence of selectred move
            if move == 0:    confidence = thisTurnProbR
            elif move == 1:  confidence = thisTurnProbP
            else:            confidence = 1.0 - (thisTurnProbR + thisTurnProbP)
            
        if Debug:
            print("Move, Confidence returned:               %i %.2f" % (move, confidence))
            input()
        
        confidence = 1 - confidence
        
        return move, confidence

    def play(self):
        move, confidence = self.predict(self.targetPredictionSize)
        
        if confidence > 1:
            confidence = 1
        
        return (move, confidence)

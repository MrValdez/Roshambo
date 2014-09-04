import BeatFrequentPick
import PatternPredictor
import rps

Debug = True
Debug = False

class PredictorSelector:
    def __init__(self):
        # PredictorSelector contains all predictors to be used
        self.Predictors = [BeatFrequentPick, PatternPredictor] 
        #self.Predictors = [PatternPredictor] 
        self.reset()
        
    def reset(self):
        self.Scores = [0] * len(self.Predictors)
        self.LastPredictor = None
        self.LastResults = []
    
    def update(self):
        self._updatePredictors()
        self._updateScore()
        
    def _updatePredictors(self):
        return
        for predictor in self.Predictors:
            predictor.update()        
    
    def _updateScore(self):
        currentTurn = rps.getTurn()
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        lost = (myMoveLastTurn == ((enemyMoveLastTurn - 1) % 3))

        # update all wins
        for i, result in enumerate(self.LastResults):
            move = result[0]
            if move == victory:
                self.Scores[i] += 2
            elif move == tie:
                self.Scores[i] += 1
            elif move == lost:
                self.Scores[i] -= 3
                
        if self.LastPredictor != None:
            i = self.LastPredictor
            move = self.LastResults[self.LastPredictor][0]
            
            if move == victory:
                self.Scores[i] += 2
            elif move == tie:
                self.Scores[i] += 1
            elif move == lost:
                self.Scores[i] -= 3

        if Debug:
            print(self.Scores)
            input()

    
    def getHighestRank(self, a):
        # 1. run each predictor.
        # 2. select the predictors with the highest confidence and score
        # 3. return the highest ranking
        
        # 1. run each predictor.
        self.LastResults = []
        results = self.LastResults 
        for predictor in self.Predictors:
            move, confidence = predictor.play(a)
            results.append((move, confidence))
            
        #return results[1]       ####################### debug
        
        # 2. select the predictors with the highest confidence and score
        index = None
        confidences = [predictor[1] for predictor in results]
                
        # add the predictor's score to its confidence
        # todo
        total = sum(self.Scores)
        if total > 0:
            for i, score in enumerate(self.Scores):
                 scoreDelta = score / total
                 confidences[i] = (confidences[i] * 0.35) + (scoreDelta * 0.65)    # todo: play with this

        # grab the highest confidence
        maxConfidence = max(confidences)
        
        # check if we have a tie for maximum. if we do, choose between them using a random number
        numCount = confidences.count(maxConfidence)
        if numCount > 1:
            division = 1 / numCount
            for i, confidence in enumerate(confidences):
                if confidence == maxConfidence:
                    confidences[i] = division
                else:
                    confidences[i] = 0
                    
            random = rps.randomRange()               
                
            for i, confidence in enumerate(confidences):
                if random <= confidence:
                    index = i
                    break
                random -= confidence
        else:
            for i, confidence in enumerate(confidences):
                if confidence == maxConfidence:
                    index = i
                    break
        
        if index == None:
            index = rps.random() % len(self.LastResults)
            confidence = 0
            results[index][1] = confidence

        if Debug:
            print (index, confidences)
        
        self.LastPredictor = index
        
        return results[index]
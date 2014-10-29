import random

import BeatFrequentPick
import PatternPredictor
import rps

Debug = True
Debug = False

class Predictor:
    def __init__(self, module, variant, name=""):
        name = module.__name__ if name == "" else name
        self.name = "%s [%s]" % (name, str(variant))
        
        self.module = module()
        self.play = self.module.play
        self.variant = variant
        self.reset()
    
    def reset(self):        
        self.score = 0
        
        self.moveLastTurn = 0
        self.confidenceLastTurn = 0
        
        self.chosenLastTurn = False

class PredictorSelector:
    """PredictorSelector contains all predictors to be used"""
    
    def __init__(self):
        Predictors = []
        
        p = Predictor(name="Pattern Predictor", module=PatternPredictor.PatternPredictor, variant="6,5,4,3,2,1")
        Predictors.append(p)
        p = Predictor(name="Pattern Predictor", module=PatternPredictor.PatternPredictor, variant="5,4,3,2,1")
        Predictors.append(p)
        p = Predictor(name="MBFP", module=BeatFrequentPick.MBFP, variant=5)
        Predictors.append(p)
        p = Predictor(name="MBFP", module=BeatFrequentPick.MBFP, variant=4)
        Predictors.append(p)
        
        self.Predictors = Predictors
        self.reset()
        
    def reset(self):
        self.LastPredictor = None
        for predictor in self.Predictors:
            predictor.reset()    
    
    def update(self):
        self._updatePredictors()
        self._updateScore()
        
    def _updatePredictors(self):
        return
        for predictor in self.Predictors:
            predictor.update()        
    
    def _updateScore(self):
        currentTurn = rps.getTurn()
        if currentTurn == 0: return
            
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)

        # update all wins        
        for predictor in self.Predictors:
            move = predictor.moveLastTurn + 1       # add +1 to move since that's the move that beats the prediction
            
            victory = (move == ((enemyMoveLastTurn + 1) % 3))
            tie = (move == enemyMoveLastTurn)
            lost = (move == ((enemyMoveLastTurn - 1) % 3))

            predictor.score *= 0.9

            if predictor.chosenLastTurn:
                # this predictor was chosen last turn, so give it bigger changes
                if victory:
                    predictor.score += 2
                elif tie:
                    predictor.score += 1
                elif lost:
                    predictor.score -= 2
            else:
                if victory:
                    predictor.score += 1
                elif tie:
                    predictor.score += 0
                elif lost:
                    predictor.score -= 1
            
            if predictor.score > 4: predictor.score = 4   
            if predictor.score < -4: predictor.score = -4   
            
            if Debug:
                if predictor.chosenLastTurn: print("** ", end="")
                print("%s: score(%.2f) move(%i)" % (predictor.name, predictor.score, move), end="")
                if victory:
                    print(" win")
                elif tie:
                    print(" tie")
                elif lost:
                    print(" lost")
        if Debug:
            input()

    
    def getHighestRank(self):
        """
        1. run each predictor.
        2. select the predictors with the highest confidence and score
        3. return the highest ranking
        """
        
        # 1. run each predictor.
        for predictor in self.Predictors:
            play = predictor.play
            variant = predictor.variant
            
            predictor.chosenLastTurn = False
            
            move, confidence = play(variant)
            predictor.moveLastTurn = move
            predictor.confidenceLastTurn = confidence

        
        ####################### debug
        
        maxScore = max([p.score for p in self.Predictors])
        if Debug: print("max score: %f " % (maxScore), end="")
        
        chosenPredictor = None
        for p in self.Predictors:
            if p.score == maxScore: 
                chosenPredictor = p
                
                if Debug: print("chosen predictor: %s" % (p.name))

                break
        
        if chosenPredictor == None:
            chosenPredictor = random.choice(self.Predictors)
            
        #chosenPredictor = self.Predictors[1]
        
        chosenPredictor.chosenLastTurn = True
        move = chosenPredictor.moveLastTurn
        confidence = chosenPredictor.confidenceLastTurn
                
        return move, confidence        ####################### debug
        
    def foo():
        #todo: broken:
        
        
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
            distribution = 1 / numCount
            for i, confidence in enumerate(confidences):
                if confidence == maxConfidence:
                    confidences[i] = distribution
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
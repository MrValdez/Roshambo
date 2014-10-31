import random
import operator

import BeatFrequentPick
import PatternPredictor
import rps

Debug = True
Debug = False

class Predictor:
    def __init__(self, module, variant, name=""):
        name = module.__name__ if name == "" else name
        self.name = "%s [%s]" % (name, str(variant))
        
        self.module = module(variant)
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

#        PPsize = 12
#        nextSeqSize = 1
#        argv = [1]

#        while PPsize > 0:
#            PPsize -= 1
#            variant = ",".join([str(s) for s in argv])
#            p = Predictor(name="Pattern Predictor", module=PatternPredictor.PatternPredictor, variant=variant)
#            Predictors.append(p)
#            nextSeqSize += 1
#            argv.append(nextSeqSize)
        
        self.Predictors = Predictors
        self.reset()
        
    def reset(self):
        self.LastPredictor = None
        for predictor in self.Predictors:
            #predictor.reset()    
            pass
    
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

        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        lost = (myMoveLastTurn == ((enemyMoveLastTurn - 1) % 3))

        # update all wins        
        for predictor in self.Predictors:
            #predictor.score *= 0.9

            if predictor.chosenLastTurn:
                # this predictor was chosen last turn, so it should go up
                if victory:
                    predictor.score += 1
                elif tie:
                    predictor.score += 0
                elif lost:
                    predictor.score += -1
            else:
                # this predictor was NOT chosen last turn, so it should go down
                if victory:
                    predictor.score += -1
                elif tie:
                    predictor.score += 0
                elif lost:
                    predictor.score += +1
                        
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
        #scoreSorted = sorted(self.Predictors, key=operator.attrgetter('score'))
        scoreSorted = self.Predictors
        
        chosenPredictor = None
        for i, predictor in enumerate(scoreSorted):
            #if i > 3: break
        
            play = predictor.play
            
            predictor.chosenLastTurn = False
            
            move, confidence = play()
            predictor.moveLastTurn = move
            predictor.confidenceLastTurn = confidence
        
        ####################### debug
        scoreSorted = sorted(self.Predictors, key=operator.attrgetter('score'))
        chosenPredictor = scoreSorted[0]
        
        if Debug:
            maxScore = max([p.score for p in self.Predictors])
            print("max score: %f " % (maxScore), end="")      
            print("chosen predictor: %s" % (chosenPredictor.name))

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
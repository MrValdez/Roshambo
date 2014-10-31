import random
import operator

import BeatFrequentPick
import PatternPredictor
import rps

Debug = True
Debug = False

class Predictor:
    def __init__(self, module, variant, name=""):
        if name == "":
            name = "%s [%s]" % (module.__name__, str(variant))
        self.name = name
        
        self.module = module(variant)
        self.play = self.module.play
        self.variant = variant
        self.reset()
    
    def reset(self):        
        self.score = 0
        
        self.moveLastTurn = 0
        self.confidenceLastTurn = 0
        
    def update(self):
        self.module.update()
        
    def play(self):
        return self.module.play()

class PredictorSelector:
    """PredictorSelector contains all predictors to be used"""
    
    def __init__(self):
        Predictors = []
        
#        p = Predictor(name="Pattern Predictor", module=PatternPredictor.PatternPredictor, variant="6,5,4,3,2,1")
#        Predictors.append(p)
#        p = Predictor(name="Pattern Predictor", module=PatternPredictor.PatternPredictor, variant="5,4,3,2,1")
#        Predictors.append(p)
        p = Predictor(module=BeatFrequentPick.MBFP, variant=5)
        Predictors.append(p)
        p = Predictor(module=BeatFrequentPick.MBFP, variant=4)
        Predictors.append(p)

        PPsize = 12
        nextSeqSize = 1
        argv = [1]

        while PPsize > 0:
            PPsize -= 1
            variant = ",".join([str(s) for s in argv])
            name = "Pattern Predictor [%i]" % (nextSeqSize)
            p = Predictor(module=PatternPredictor.PatternPredictor, variant=variant, name=name)
            Predictors.append(p)
            nextSeqSize += 1
            argv.append(nextSeqSize)
        
        self.Predictors = Predictors
        self.reset()
        
    def reset(self):
        self.LastPredictor = None
        self.LastYomiLayer = 0
        for predictor in self.Predictors:
            #predictor.reset()    
            pass
    
    def update(self):
        self._updateScore()
            
    def _updateScore(self):
        currentTurn = rps.getTurn()
        if currentTurn == 0: return
            
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)

        # update predictor used last turn
        if self.LastPredictor:
            predictor = self.LastPredictor

            victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
            tie = (myMoveLastTurn == enemyMoveLastTurn)
            lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)

            if Debug:
                print("**%s: move(%i) score(%.2f)" % (predictor.name, predictor.moveLastTurn, predictor.score), end="")
                if victory:
                    print(" win")
                elif tie:
                    print(" tie")
                elif lost:
                    print(" lost")

            if victory:
                predictor.score += 1
            elif tie:
                predictor.score += 0
            elif lost:
                predictor.score += -1

        # update the rest of the predictors that they should have gained if they were chosen
        for predictor in self.Predictors:
            if self.LastPredictor == predictor:
                continue
            #predictor.score *= 0.9

            myMoveLastTurn = (predictor.moveLastTurn + self.LastYomiLayer + 1) % 3
            victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
            tie = (myMoveLastTurn == enemyMoveLastTurn)
            lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
        
            if Debug:
                print("%s: move(%i) score(%.2f)" % (predictor.name, predictor.moveLastTurn, predictor.score), end="")
                if victory:
                    print(" win")
                elif tie:
                    print(" tie")
                elif lost:
                    print(" lost")

            if victory:
                predictor.score += +1
            elif tie:
                predictor.score += 0
            elif lost:
                predictor.score += -1
    
    def getHighestRank(self):
        """
        1. run each predictor.
        2. select the predictors with the highest confidence and score
        3. return the highest ranking
        """
        
        # 1. run each predictor.
        scoreSorted = sorted(self.Predictors, key=operator.attrgetter('score'))
        #scoreSorted = self.Predictors
        
        chosenPredictor = None
        self.LastPredictor = None
        for i, predictor in enumerate(scoreSorted):                  
            predictor.update()
            
            move, confidence = predictor.play()
            predictor.moveLastTurn = move
            predictor.confidenceLastTurn = confidence
        
        #2. select the predictors with the highest confidence and score
        ####################### debug
        scoreSorted = sorted(self.Predictors, key=operator.attrgetter('score'), reverse=True)
        chosenPredictor = scoreSorted[0]
        
        if Debug:
            maxScore = max([p.score for p in self.Predictors])                
            print("max score: %f " % (maxScore), end="")      
            print("chosen predictor: %s" % (chosenPredictor.name))
            input()

        if chosenPredictor == None:
            chosenPredictor = random.choice(self.Predictors)
            
        #chosenPredictor = self.Predictors[1]
        
        self.LastPredictor = chosenPredictor
        move = chosenPredictor.moveLastTurn
        confidence = chosenPredictor.confidenceLastTurn
                
        #3. return the highest ranking
        return move, confidence        
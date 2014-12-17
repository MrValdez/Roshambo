import operator
import math

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
        self.scoreWins = 0
        self.scoreLosts = 0
        
        self.moveLastTurn = 0
        self.confidenceThisTurn = 0
        self.confidenceLastTurn = 0
        
    def update(self):
        self.module.update()
        
    def play(self):
        return self.module.play()

class PredictorSelector:
    """PredictorSelector contains all predictors to be used"""
    
    def __init__(self):
        Predictors = []
        
#        p = Predictor(module=PatternPredictor.PatternPredictor, variant="6,5,4,3,2,1")
#        Predictors.append(p)
#        p = Predictor(module=PatternPredictor.PatternPredictor, variant="5,4,3,2,1")
#        Predictors.append(p)
#        p = Predictor(module=BeatFrequentPick.MBFP, variant=5)
#        Predictors.append(p)
#        p = Predictor(module=BeatFrequentPick.MBFP, variant=4)
#        Predictors.append(p)

        PPsize = 29
        nextSeqSize = 1
        argv = [1]

        while PPsize > 0:
            variant = ",".join([str(s) for s in argv])
            name = "Pattern Predictor [%i]" % (nextSeqSize)
            p = Predictor(module=PatternPredictor.PatternPredictor, variant=variant, name=name)
#            if PPsize + 1== 5 or PPsize +1== 9:
#                Predictors.append(p)
            Predictors.append(p)
            nextSeqSize += 1
            argv.append(nextSeqSize)
            PPsize -= 1

        MBFPsize = 21
        while MBFPsize > 0:
            p = Predictor(module=BeatFrequentPick.MBFP, variant=MBFPsize)
            #Predictors.append(p)
            MBFPsize -= 1
        
        self.Predictors = Predictors
        self.reset()
        
    def reset(self):
        self.LastPredictor = None
        self.LastYomiLayer = 0
        # note: resetting against each AI seems to give a better rank. study this further
        for predictor in self.Predictors:
            predictor.reset()    
            
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
                print("**%s: move(%i) score(+%i/-%i) confidence(%.2f/%.2f)" % (predictor.name, predictor.moveLastTurn, predictor.scoreWins, predictor.scoreLosts, predictor.confidenceThisTurn, predictor.confidenceLastTurn), end="")
                if victory:
                    print(" win")
                elif tie:
                    print(" tie")
                elif lost:
                    print(" lost")

            if victory:
                predictor.scoreWins += 1
            elif tie:
                predictor.scoreWins += 1
                predictor.scoreLosts += 0
            elif lost:
                predictor.scoreLosts += 1
        
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
                print("%s: move(%i) score(+%i/-%i) confidence(%.2f/%.2f)" % (predictor.name, predictor.moveLastTurn, predictor.scoreWins, predictor.scoreLosts, predictor.confidenceThisTurn, predictor.confidenceLastTurn), end="")
                if victory:
                    print(" win")
                elif tie:
                    print(" tie")
                elif lost:
                    print(" lost")

            if victory:
                predictor.scoreWins += 1
            elif tie:
                predictor.scoreWins += 1
                predictor.scoreLosts += 0
            elif lost:
                predictor.scoreLosts += 1
    
    def getPrediction(self):
        """
        1. run each predictor.
        2. select the predictors with the highest confidence and score
        3. return the highest ranking
        """
        
        # 1. run each predictor.
        #scoreSorted = sorted(self.Predictors, key=operator.attrgetter('score'))
        scoreSorted = self.Predictors
        
        chosenPredictor = None
        self.LastPredictor = None
        for i, predictor in enumerate(scoreSorted):                  
            predictor.update()
            
            move, confidence = predictor.play()
            predictor.moveLastTurn = move
            
            #confidence = round(confidence, 2)   # round to the nearest 2 decimals
            
            #if confidence > 0.9: confidence = 0.9
        
            predictor.confidenceLastTurn = predictor.confidenceThisTurn
            predictor.confidenceThisTurn = confidence
            
        #2. select the predictors with the highest confidence and score
        move, confidence = self.getHighestRank()
        
        #3. return the highest ranking
        return move, confidence
        
    def getHighestRank(self):    
        chosenPredictor, rankRating = self.getHighestRank_LowerWilson()
        #chosenPredictor, rankRating = self.getHighestRank_Naive()
        
        self.LastPredictor = chosenPredictor
        move = chosenPredictor.moveLastTurn
        predictorConfidence = chosenPredictor.confidenceThisTurn

        confidence = rankRating
                
        return move, confidence 
    
    def getHighestRank_LowerWilson(self):
        """
        Get the highest rank using "lower bound of Wilson score confidence interval for a Bernoulli parameter"
        http://www.evanmiller.org
         How Not To Sort By Average Rating.htm
        """

        # grab the top 3 wins, top 3 wins-lost, top 3 confidences
        maxWins       = sorted(self.Predictors, key=lambda i: i.scoreWins)
        maxDiff       = sorted(self.Predictors, key=lambda i: i.scoreWins - i.scoreLosts)
        maxConfidence = sorted(self.Predictors, key=lambda i: i.confidenceThisTurn)
        
        # grab the top predictors by wins, diffs and confidence.
        # on test, this has worse effect on ranking. (need more testing for confirmation)
        filteredPredictors = self.Predictors    # no union
        #filteredPredictors = set(maxWins[:3]) | set(maxDiff[:3]) | set(maxConfidence[:3])   # union
        #filteredPredictors = set(maxWins[:5]) | set(maxDiff[:5]) | set(maxConfidence[:5])   # union
        

##############
##todo: add treshold instead?
#########
        
        predictorScores = []
        for i, predictor in enumerate(filteredPredictors):
            positiveRatings = predictor.scoreWins
            totalRatings = predictor.scoreWins + predictor.scoreLosts
            confidence = predictor.confidenceThisTurn

#            if confidence >= 1:                             # possible DNA
#                predictorScores.append((1.0, predictor))
#                continue
                        
            confidence = 1 - confidence
            maxPredictionRating = 0.99                      # possible DNA
            if confidence > maxPredictionRating: confidence = maxPredictionRating
            if confidence < 0.0: confidence = 0.0
            #confidence = 0.85            
                        
            if positiveRatings <= 0 or totalRatings <= 0:
                continue
                        
            #z = 1.96        # hardcorded for confidence=95%
            #z = 1.0         # 1.44=85% 1.96=95%
            p = 1 - 0.5 * (1 - confidence)
            #z = cached_normcdfi(p)
            z = rps.normcdfi(p)
            
            phat = float(positiveRatings) / totalRatings
            n = totalRatings
            
            rating = (phat + z*z/(2*n) - z * math.sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)        
            
            #print(confidence,positiveRatings, rating)
            predictorScores.append((rating, predictor))

        if len(predictorScores):
            # filter out predictors that does not tie with the maximum rating, for optimization purposes
            maxRating = max(predictorScores, key=lambda i: i[0])[0]
            p = [p for p in predictorScores if p[0] == maxRating]

            if predictorScores[0] != maxRating:
                assert("Something is wrong. We filtered out predictions that is not the maximum but we got some here")                
            
            predictorScores = p
        else:
            random = rps.random() % len(filteredPredictors)
            chosenPredictor = filteredPredictors[random]
            rating = 0
            
        if len(predictorScores) == 1:
            rating, chosenPredictor = predictorScores[0]
        elif len(predictorScores) > 1:      
            # check if the highest rating predictions have different moves.
            # if True, then randomly select from between the moves
            Rmoves = [p for p in predictorScores if p[1].moveLastTurn == 0]
            Pmoves = [p for p in predictorScores if p[1].moveLastTurn == 1]
            Smoves = [p for p in predictorScores if p[1].moveLastTurn == 2]
            size = len(predictorScores)
                        
            # play the move with the highest score
            finalChoice = None
            if len(Rmoves) and len(Rmoves) > len(Pmoves) and len(Rmoves) > len(Smoves):
                finalChoice = Rmoves[0]
            elif len(Pmoves) and len(Pmoves) > len(Rmoves) and len(Pmoves) > len(Smoves):
                finalChoice = Pmoves[0]
            elif len(Smoves) and len(Smoves) > len(Pmoves) and len(Smoves) > len(Rmoves):
                finalChoice = Smoves[0]
            else:
                random = rps.random() % len(predictorScores)
                finalChoice = predictorScores[random]
            
            chosenPredictor = finalChoice[1]
            rating = finalChoice[0]            
            
        if 0 or Debug:
            print("currentTurn", rps.getTurn())
            for p in predictorScores:
                print ("%s (%i) Wilson Rating: %.3f. Confidence: %.3f Score +%i/-%i" % (p[1].name, p[1].moveLastTurn, p[0], p[1].confidenceThisTurn, p[1].scoreWins, p[1].scoreLosts))
        
            if len(predictorScores):
                input()         

        return chosenPredictor, rating
    
    def getHighestRank_Naive(self):
        """Get the highest rank using a naive algo"""

        # filter out low confidences
        maxConfidence = max(self.Predictors, key=operator.attrgetter('confidenceThisTurn'))
        
        # grab the predictors close to the confidence
        p = [p for p in self.Predictors if p.confidenceThisTurn >= maxConfidence.confidenceThisTurn * 0.75]
        
        if len(p) == 1:
            # only one predictor has high confidence
            chosenPredictor = p[0]
        elif len(p) > 1:
            # many predictors has high confidence. look for highest wins
            maxScore = max(p, key=operator.attrgetter('scoreWins'))
            predictors = p
            p = [p for p in predictors if p.scoreWins >= maxScore.scoreWins * 0.75]
            
            if len(p) == 1:
                chosenPredictor = p[0]
            elif len(p) > 1:
                # there are ties. look for lowest losts
                maxScore = min(p, key=operator.attrgetter('scoreLosts'))
                predictors = p
                p = [p for p in predictors if p.scoreLosts == maxScore]
                
                if len(p) == 1:
                    chosenPredictor = p[-1]
                elif len(p) > 1:
                    # choose at random
                    random = rps.random() % len(p)
                    chosenPredictor = p[random]
            
            if len(p) == 0:
                maxConfidence = max(self.Predictors, key=operator.attrgetter('confidenceThisTurn'))
                p = [p for p in self.Predictors if p.confidenceThisTurn >= maxConfidence.confidenceThisTurn]
                
                random = rps.random() % len(p)
                chosenPredictor = p[random]
        else:
            # confidences are low. look for highest wins
            maxScore = max(self.Predictors, key=operator.attrgetter('scoreWins'))
            p = [p for p in self.Predictors if p.scoreWins == maxScore]
            
            if len(p) == 1:
                chosenPredictor = p[0]
            elif len(p) > 1:
                # choose at random
                random = rps.random() % len(p)
                chosenPredictor = p[random]
            else:
                # choose at random
                random = rps.random() % len(self.Predictors)
                chosenPredictor = self.Predictors[random]
                    
        if Debug:
            maxScore = max([p.scoreWins for p in self.Predictors])                
            print("max score: %f " % (maxScore), end="")      
            maxScore = max([p.confidenceThisTurn for p in self.Predictors])                
            print("max confidence: %f " % (maxScore), end="")      
            print("chosen predictor: %s" % (chosenPredictor.name))
            input()

            
        rankConfidence = chosenPredictor.confidenceThisTurn
        return chosenPredictor, rankConfidence
        
# from stackoverflow. google search: "wilson bernoulli python". (No exact url because I was on mobile Internet and I copy-pasted from phone to pc)

def binconf(p, n, c=0.95):
    '''
    Calculate binomial confidence interval based on the number of positive and
    negative events observed. Uses Wilson score and approximations to inverse
    of normal cumulative density function.

    Parameters
    ----------
    p: int
    number of positive events observed
    n: int
    number of negative events observed
    c : optional, [0,1]
    confidence percentage. e.g. 0.95 means 95% confident the probability of
    success lies between the 2 returned values

    Returns
    -------
    theta_low : float
    lower bound on confidence interval
    theta_high : float
    upper bound on confidence interval
    '''
    p, n = float(p), float(n)
    N = p + n

    if N == 0.0: return (0.0, 1.0)

    p = p / N
    z = normcdfi(1 - 0.5 * (1-c))

    a1 = 1.0 / (1.0 + z * z / N)
    a2 = p + z * z / (2 * N)
    a3 = z * math.sqrt(p * (1-p) / N + z * z / (4 * N * N))

    return (a1 * (a2 - a3), a1 * (a2 + a3))


def erfi(x):
    """Approximation to inverse error function"""
    a = 0.147 # MAGIC!!!
    a1 = math.log(1 - x * x)
    a2 = (2.0 / (math.pi * a) + a1 / 2.0)

    return (sign(x) * math.sqrt( math.sqrt(a2 * a2 - a1 / a) - a2 ))


def sign(x):
    if x < 0: return -1
    if x == 0: return 0
    if x > 0: return 1

def normcdfi(p, mu=0.0, sigma2=1.0):
    """Inverse CDF of normal distribution"""
    if mu == 0.0 and sigma2 == 1.0:
        return math.sqrt(2) * erfi(2 * p - 1)
    else:
        return mu + math.sqrt(sigma2) * normcdfi(p)

CacheForNormCDFISet = []
def cached_normcdfi(p, mu=0.0, sigma2=1.0):
    """Call normcdfi and cache the results"""
    global CacheForNormCDFISet 
    for i in CacheForNormCDFISet:
        if i[1] == p and i[2] == mu and i[3] == sigma2: return i[0]
    
    # p is not in cache. Add it
    result = normcdfi(p, mu, sigma2)
    
    cache = (result, p, mu, sigma2)
    CacheForNormCDFISet.append(cache)
    
    return result
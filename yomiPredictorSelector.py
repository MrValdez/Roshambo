import operator
import math

import BeatFrequentPick
import PatternPredictor
import justRock
import rps

import random
from pprint import pprint

Debug = True
Debug = False

# opcode
scoreBufferWin  = 0
scoreBufferLost = 1

# implementations
useScoreBuffer = True
useScoreBuffer = False

scoreReset = False      # perform badly
scoreReset = True       

class Predictor:
    def __init__(self, module, variant, name=""):
        if name == "":
            name = "%s [%s]" % (module.__name__, str(variant))
        self.name = name
        
        self.module = module(variant)
        self.play = self.module.play
        self.variant = variant

        self.scoreWins = 0
        self.scoreLosts = 0
        self.totalTurns = 0
        
        self.scoreBuffer = []
        self.scoreBufferSize = 300
        
        self.reset()
    
    def addWins(self, points):
        self.scoreWins += points
        self.scoreBuffer.extend([scoreBufferWin] * points)
        self.scoreBuffer = self.scoreBuffer[-self.scoreBufferSize:]
    
    def addLosts(self, points):
        self.scoreLosts += points
        self.scoreBuffer.extend([scoreBufferLost] * points)
        self.scoreBuffer = self.scoreBuffer[-self.scoreBufferSize:]
    
    def reset(self):        
        if scoreReset:
            self.scoreBuffer = []
            self.scoreWins = 0
            self.scoreLosts = 0
            self.totalTurns = 0

        self.moveLastTurn = 0
        self.confidence = 0
        self.rankingConfidence = 0
        
    def update(self):
        self.totalTurns += 1
        self.module.update()
        
    def play(self):
        return self.module.play()

class PredictorSelector:
    """PredictorSelector contains all predictors to be used"""
    
    def __init__(self, dna):
        Predictors = []
        
        for predictor in dna.predictors:
            if predictor == "none":   
                continue
                
            if predictor.find(" ") > 0:
                # Predictor has variant
                name, value = predictor.split(" ")
                value = int(value)
            else:
                # Predictor has no variant
                name, value = predictor, None
            
            p = None
            if name == "pp":
                variant = ",".join([str(s + 1) for s in range(value)])
                name = "Pattern Predictor [%i]" % (value)
                p = Predictor(module=PatternPredictor.PatternPredictor, variant=variant, name=name)
            elif name == "mbfp":
                p = Predictor(module=BeatFrequentPick.MBFP, variant=value)
            elif name == "rock":
                p = Predictor(module=justRock.Rock, variant=None)
                
            if p != None:
                Predictors.append(p)

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

            if victory:
                predictor.addWins(1)
            elif tie:
                predictor.addWins(1)
                predictor.addLosts(0)
            elif lost:
                predictor.addLosts(1)

        # update the rest of the predictors that they should have gained if they were chosen
        for predictor in self.Predictors:
            if self.LastPredictor == predictor:
                continue
            #predictor.score *= 0.9

            if self.LastYomiLayer == -1:
                myMoveLastTurn = (predictor.moveLastTurn + 1) % 3
            else:
                myMoveLastTurn = (predictor.moveLastTurn + self.LastYomiLayer + 1) % 3

            victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
            tie = (myMoveLastTurn == enemyMoveLastTurn)
            lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
        
            if victory:
                predictor.addWins(1)
            elif tie:
                predictor.addWins(1)
                predictor.addLosts(0)
            elif lost:
                predictor.addLosts(1)
                        
        if Debug:
            print("Turn:", currentTurn - 1)
            print("Enemy Move last turn:", enemyMoveLastTurn)
            print(" " * 25 + "move layeredMove score confidence ranking")
            #for predictor in reversed(sorted(self.Predictors, key=operator.attrgetter('rankingConfidence'))):
            for predictor in sorted(self.Predictors, key=operator.attrgetter('rankingConfidence')):
                if self.LastYomiLayer == -1:
                    myMoveLastTurn = (predictor.moveLastTurn + 1) % 3
                else:
                    myMoveLastTurn = (predictor.moveLastTurn + self.LastYomiLayer + 1) % 3
                
                victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
                tie = (myMoveLastTurn == enemyMoveLastTurn)
                lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
                
                print("%s: %i %i (+%i/-%i) %.2f %f" % 
                    (predictor.name.ljust(24), predictor.moveLastTurn, myMoveLastTurn, predictor.scoreWins, predictor.scoreLosts, predictor.confidence, predictor.rankingConfidence), end="")
                if victory:
                    print(" win", end="")
                elif tie:
                    print(" tie", end="")
                elif lost:
                    print(" lost", end="")
                if predictor == self.LastPredictor:
                    print (" **", end="")
                print("")
            input()
    
    def getPrediction(self, dna):
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
        
            predictor.confidence = confidence
            
        #2. select the predictors with the highest confidence and score
        move, confidence = self.getHighestRank(dna)
        
#        predictor = self.LastPredictor
#        print("%s: %i (+%i/-%i) %.2f %f" % (predictor.name.ljust(24), predictor.moveLastTurn,predictor.scoreWins, predictor.scoreLosts, predictor.confidence, predictor.rankingConfidence))

        #3. return the highest ranking
        return move, confidence
        
    def getHighestRank(self, dna):              
        if dna.predictor_ranking == "wilson-high":
            chosenPredictor, rankRating = self.getHighestRank_LowerWilson(higherBound = True)
        elif dna.predictor_ranking == "wilson-low":
            chosenPredictor, rankRating = self.getHighestRank_LowerWilson(higherBound = False)
#        elif dna.predictor_ranking == "toilet":
#            chosenPredictor, rankRating = self.getHighestRank_Toilet()
        elif dna.predictor_ranking == "naive":
            chosenPredictor, rankRating = self.getHighestRank_Naive()
        else:
            chosenPredictor, rankRating = None, 0
            return 0, 0

        self.LastPredictor = chosenPredictor
        move = chosenPredictor.moveLastTurn
        predictorConfidence = chosenPredictor.confidence
        confidence = rankRating
        
        return move, confidence 
    
    def getHighestRank_LowerWilson(self, higherBound = True):
        """
        Get the highest rank using "lower bound of Wilson score confidence interval for a Bernoulli parameter"
        http://www.evanmiller.org
         How Not To Sort By Average Rating.htm
        
        https://news.ycombinator.com/item?id=3792627
        """
        
        if len(self.Predictors) == 1:
            # there is only one predictor. choose that immediately
            predictor = self.Predictors[0]
            return (predictor, predictor.confidence)
        
        # grab the top 3 wins, top 3 wins-lost, top 3 confidences
#        maxWins       = sorted(self.Predictors, key=lambda i: i.scoreWins)
#        maxDiff       = sorted(self.Predictors, key=lambda i: i.scoreWins - i.scoreLosts)
#        maxConfidence = sorted(self.Predictors, key=lambda i: i.confidence)
        
        # grab the top predictors by wins, diffs and confidence.
        # on test, this has worse effect on ranking. (need more testing for confirmation)
        filteredPredictors = self.Predictors    # no union

        # warning: set is non-deterministic
        #filteredPredictors = set(maxWins[:3]) | set(maxDiff[:3]) | set(maxConfidence[:3])   # union
        #filteredPredictors = set(maxWins[:5]) | set(maxDiff[:5]) | set(maxConfidence[:5])   # union
        #filteredPredictors = list(filteredPredictors)
        
##############
##todo: add treshold instead?
#########
        
        predictorScores = []
        for i, predictor in enumerate(filteredPredictors):

            if useScoreBuffer == False:
                positiveRatings = predictor.scoreWins
                negativeRatings = predictor.scoreLosts
                totalRatings    = predictor.totalTurns
                totalRatings    = positiveRatings + negativeRatings
            else:
                positiveRatings = predictor.scoreBuffer.count(scoreBufferWin)
                negativeRatings = predictor.scoreBuffer.count(scoreBufferLost)
                totalRatings    = len(predictor.scoreBuffer)
                totalRatings    = positiveRatings + negativeRatings
                
            confidence = predictor.confidence
            
            # experiment: what happens if we use our score as confidence in self?
            
#            if confidence >= 1:                             # possible DNA
#                predictorScores.append((1.0, predictor))
#                continue
                                                
            if positiveRatings <= 0 or totalRatings <= 0:
                continue
                
            if 1:
                #confidence = 1 - confidence
                maxPredictionRating = 0.99                      # possible DNA
                #maxPredictionRating = 1                      # possible DNA
                
                if confidence > maxPredictionRating: confidence = maxPredictionRating
                if confidence < 0.0: confidence = 0.0

                ratings = rps.binconf(positiveRatings, negativeRatings, confidence)
                #ratings = binconf(positiveRatings, negativeRatings, confidence)
                
                if higherBound:
                    rating = float(ratings[1])
                else:
                    rating = float(ratings[0])
                    
                #rating += (ratings[1] - ratings[0]) / 2
                
                if math.isnan(rating): rating = 0
                
                rating = round(rating,3)        # fix for conversion from C float to Python float                
            else:
                maxPredictionRating = 0.99                      # possible DNA
                #maxPredictionRating = 1                      # possible DNA
                if confidence > maxPredictionRating: confidence = maxPredictionRating
                if confidence < 0.0: confidence = 0.0
                
                #z = 1.96        # hardcorded for confidence=95%
                #z = 1.0         # 1.44=85% 1.96=95%
                p = 1 - 0.5 * (1 - confidence)
                z = cached_normcdfi(p)
                #z = rps.normcdfi(p)
                
                phat = float(positiveRatings) / totalRatings
                n = totalRatings
                
                rating = (phat + z*z/(2*n) - z * math.sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)
            
            #rating = round(rating, 3)   # round to the nearest 3 decimals. experiment
            
            predictor.rankingConfidence = rating
            predictorScores.append((rating, predictor))

        if len(predictorScores) > 1:
            # filter out predictors that does not tie with the maximum rating, for optimization purposes
            maxRating = max(predictorScores, key=lambda i: i[0])[0]
            p = [p for p in predictorScores if p[0] == maxRating]

            if predictorScores[0] != maxRating:
                assert("Something is wrong. We filtered out predictions that is not the maximum but we got some here")                
            
            predictorScores = p
        elif len(predictorScores) == 1:
            rating, chosenPredictor = predictorScores[0]
            return chosenPredictor, rating
        else:
            random = rps.random() % len(filteredPredictors)
            chosenPredictor = filteredPredictors[random]
            rating = 0
            return chosenPredictor, rating
            
        # there are multiple predictors with the same rating.
        # let's choose the one with the biggest score (positive - negative)
        if useScoreBuffer == False:
            highestScorers = max(predictorScores, key=lambda i: i[1].scoreWins)
        else:
            highestScorers = max(predictorScores, key=lambda i: i[1].scoreBuffer.count(scoreBufferWin))
        predictorScores = [p for p in predictorScores if p[0] == highestScorers[0]]

        # tally the moves and choose the move with the most tally
        
        tally = [0, 0, 0]
        for p in predictorScores:
            # tally[p[1].moveLastTurn] += 1
            if p[1].moveLastTurn == 0: tally[0] += 1
            if p[1].moveLastTurn == 1: tally[1] += 1
            if p[1].moveLastTurn == 2: tally[2] += 1
                
        # let's choose a move at random between them        
        # Filter predictorScores to only include the predictors with the maximum tally.
        maxTally = max(tally)
        talliedScorers = []
        if tally[0] == maxTally: 
            rocks = [talliedScorers.append(p) for p in predictorScores if p[1].moveLastTurn == 0]
        if tally[1] == maxTally: 
            papers = [talliedScorers.append(p) for p in predictorScores if p[1].moveLastTurn == 1]
        if tally[2] == maxTally: 
            scissors = [talliedScorers.append(p) for p in predictorScores if p[1].moveLastTurn == 2]               
                        
        if len(talliedScorers) == 1:
            # in practice, this doesn't happen, but we put in this option to try to minimize bugs
            rating, chosenPredictor = talliedScorers[0]
        else:
            # play the move with the highest score
            finalChoice = None
            
            if tally[0] and tally[0] > tally[1] and tally[0] > tally[2]:
                Rmoves = [p for p in talliedScorers if p[1].moveLastTurn == 0]
                finalChoice = Rmoves[0]
            elif tally[1] and tally[1] > tally[0] and tally[1] > tally[2]:
                Pmoves = [p for p in talliedScorers if p[1].moveLastTurn == 1]
                finalChoice = Pmoves[0]
            elif tally[2] and tally[2] > tally[0] and tally[2] > tally[1]:
                Smoves = [p for p in talliedScorers if p[1].moveLastTurn == 2]
                finalChoice = Smoves[0]
            else:               
                # there are still ties so we choose at random
                random = rps.random() % len(talliedScorers)
                finalChoice = talliedScorers[random]
            
            chosenPredictor = finalChoice[1]
            rating = finalChoice[0]            
        
        if Debug:
            currentTurn = rps.getTurn()
            print("currentTurn", currentTurn)
            for p in talliedScorers:
                print ("%s (%i) Wilson Rating: %.3f. Confidence: %.3f Score +%i/-%i" % (p[1].name, p[1].moveLastTurn, p[0], p[1].confidence, p[1].scoreWins, p[1].scoreLosts))
                
            input()         

        return chosenPredictor, rating

    def getHighestRank_Toilet(self):
        """Get the highest rank using a TOILET algo"""

        # filter out low confidences
        #maxConfidence = max(self.Predictors, key=operator.attrgetter('confidence'))
        #p = [p for p in self.Predictors if p.confidence == maxConfidence]
        
        
        p = self.Predictors
        
        if len(p) == 1:
            # only one predictor has high confidence
            chosenPredictor = p[0]
        elif len(p) > 1:
            random.shuffle(p, random = rps.randomRange)
            
            # drop the first 37% and grab the best 
            drop = round(len(p) * 0.37) - 1
            initial = p[:drop]
            maxConfidence = max(initial, key=operator.attrgetter('confidence'))
            maxConfidence = maxConfidence.confidence
            
            toCheck = p[drop:]
            for p in toCheck:
                if p.confidence >= maxConfidence:
                    chosenPredictor = p
                    break
            else:
                chosenPredictor = toCheck[-1]
            
        rankConfidence = chosenPredictor.confidence
        return chosenPredictor, rankConfidence
            
    def getHighestRank_Naive(self):
        """Get the highest rank using a naive algo"""

        # filter out low confidences
        maxConfidence = max(self.Predictors, key=operator.attrgetter('confidence'))
        p = [p for p in self.Predictors if p.confidence >= maxConfidence.confidence]
        
        if len(p) == 1:
            # only one predictor has high confidence
            chosenPredictor = p[0]
        elif len(p) > 1:
            # many predictors has high confidence. look for highest wins
            maxScore = max(p, key=operator.attrgetter('scoreWins'))
            
#            maxScore = 0
#            for pred in p:
#                maxScore = max(maxScore, pred.scoreWins - pred.scoreLosts)            
            
            predictors = p
            p = [p for p in predictors if p.scoreWins >= maxScore.scoreWins]
            
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
                maxConfidence = max(self.Predictors, key=operator.attrgetter('confidence'))
                p = [p for p in self.Predictors if p.confidence >= maxConfidence.confidence]
                
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
            maxScore = max([p.confidence for p in self.Predictors])                
            print("max confidence: %f " % (maxScore), end="")      
            print("chosen predictor: %s" % (chosenPredictor.name))
            #input()

            
        rankConfidence = chosenPredictor.confidence
        return chosenPredictor, rankConfidence
        
# http://stackoverflow.com/questions/10029588/python-implementation-of-the-wilson-score-interval

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
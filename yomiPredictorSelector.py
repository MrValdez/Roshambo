if False:
    # select from the predictors based on highest confidence
    # todo: select from the predictors based on past performance
    
    global lastSelectedPrediction
    if rps.getTurn() == 0: 
        # create the predictors scorecard
        global predictorsScoreCard
        predictorsScoreCard = [0] * len(predictors)
    elif lastSelectedPrediction != -1:    
        # update scorecard
        currentTurn = rps.getTurn()
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        victory = (myMoveLastTurn == ((enemyMoveLastTurn + 1) % 3))
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        if victory:
            predictorsScoreCard[lastSelectedPrediction] += 1
        elif tie:
            predictorsScoreCard[lastSelectedPrediction] += 0
        else:
            predictorsScoreCard[lastSelectedPrediction] -= 1

    # select best performer
    bestPerformance = max(predictorsScoreCard)
    bestPerformanceIndex = -1
    if bestPerformance > 0:
        for i, performance in enumerate(predictorsScoreCard):
            if bestPerformance == performance:
                bestPerformanceIndex = i          
                break
        
    # select highest rate
    rates = [predictor[1] for predictor in predictors]
    highestRate = max(rates)
    highestRateIndex = -1
    if highestRate > predictors[bestPerformanceIndex][1]:
        for i, predictor in enumerate(predictors):
            if highestRate == predictor[1]:
                highestRateIndex = i          
                break
    
    # choose between two
    if highestRateIndex == -1:
        selectedPrediction = bestPerformanceIndex
    elif bestPerformanceIndex == -1:
        selectedPrediction = highestRateIndex
    elif bestPerformanceIndex == -1 and highestRateIndex == -1:
        selectedPrediction = rps.random() % 2
    elif bestPerformanceIndex == highestRateIndex:
        selectedPrediction = highestRateIndex
    else:
        prob = rps.randomRange()
        if prob < predictors[bestPerformanceIndex][1]:
            selectedPrediction = bestPerformanceIndex
        else:
            selectedPrediction = highestRateIndex
            
    prediction = predictors[selectedPrediction]
    lastSelectedPrediction = selectedPrediction

    # end selection


# PredictorScores contains all predictors
import BeatFrequentPick
import PatternPredictor
import rps

Debug = True
Debug = False

class PredictorSelector:
    def __init__(self):
        self.Predictors = [BeatFrequentPick, PatternPredictor] 
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
                self.Scores[i] -= 1
            
        return

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
            
        #return results[1]       # debug        
        
        # 2. select the predictors with the highest confidence and score
        index = None
        confidences = [predictor[1] for predictor in results]
        #self.LastPredictor = index
        
        # add the predictor's score to its confidence
        total = sum(self.Scores)
        if total > 0:
            for i, score in enumerate(self.Scores):
                 scoreDelta = score / total
                 confidences[i] = (confidences[i] * 0.5) + (scoreDelta * 0.5)
        
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
        return results[index]
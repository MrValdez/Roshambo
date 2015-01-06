import rps
import math

class RPSstrategy:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # playerWins and playerLosts refer to the AI's current score and not to this strategy's personal score
        self.playerWins = 0
        self.playerLosts = 0
        self.playerTies = 0
        
        self.strategyWins = 0
        self.strategyLosts = 0
        self.strategyTies = 0
        
        self.moveLastTurn = 0
        
        #self.losingValue = 100       # if the lost difference reaches this value, the AI is losing  # rank 8.6
        self.losingValue = 50       # if the lost difference reaches this value, the AI is losing    # rank 5.6
        self.panicValue = int(self.losingValue * 0.75) #37  # dna
        self.panicValue = 3 * 3 * 3 #27
        self.panicValue = 1000  # 9.9.7643
        self.panicValue = 300   # 8.10.7551
        self.panicValue = 500   # 7.9.7643
        self.panicValue = 100   # 7.9.7643
        self.panicValue = 84    # 8.9.7464
        self.panicValue = 83    # 8.6.7864
        self.panicValue = 80    # 6.7.7568
        self.panicValue = 75    # 8.6.7946
        self.panicValue = 73    # 7.8.7536
        self.panicValue = 72    # 7.9.7315
        self.panicValue = 68    # 8.6.8458
        self.panicValue = 67    # 8.5.8524
        self.panicValue = 56    # 7.6.8367
        self.panicValue = 47    # 10.6.8033
        self.panicValue = 12    # 10.6.7924
        self.panicValue = 7     # 8.6.8164
        self.panicValue = 4     # 4.6.7939
        self.panicValue = 29    # 3.7/5.8
        self.panicValue = 13    # 4.8
        self.panicValue = 37    # 4.5.8347                
        
        self.panicValue = 2
    
    def update(self):        
        currentTurn = rps.getTurn()
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)

        victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
        
        if victory:
            self.playerWins += 1
        elif tie:
            self.playerTies += 1
        elif lost:
            self.playerLosts += 1

        myMoveLastTurn = self.moveLastTurn
        victory = (myMoveLastTurn == (enemyMoveLastTurn + 1) % 3)
        tie = (myMoveLastTurn == enemyMoveLastTurn)
        lost = (myMoveLastTurn == (enemyMoveLastTurn - 1) % 3)
        
        if victory:
            self.strategyWins += 1
        elif tie:
            self.strategyLosts += 1
        elif lost:
            self.strategyTies += 1
    
    def play(self):
        move = rps.random() % 3           
        confidence = 0
#        return move, confidence
        
        totalTurns = 1000
        currentTurn = rps.getTurn()
        turnsRemaining = totalTurns - currentTurn
        lostDifference = self.playerLosts - self.playerWins
        #lostDifference = self.playerLosts + (self.playerTies /2)- self.playerWins  # doesn't work
        #lostDifference = self.playerLosts + (self.playerTies )- self.playerWins  # doesn't work
        
        EarlyGame = 20      # DNA   (17-21)
        if currentTurn == 0:
            confidence = 1
        elif currentTurn < EarlyGame:
            # at the beginning of the game, we use our own play since we don't have enough information
            # to predict
            #if self.playerWins < self.losingValue:
                #confidence = currentTurn / EarlyGame
                #confidence = math.log(currentTurn, EarlyGame)
#                confidence = 1 - (currentTurn / EarlyGame)
                confidence = 1 - math.log(currentTurn, EarlyGame)
#        elif 1 and lostDifference > 1 and currentTurn >= totalTurns - lostDifference + (self.playerTies * 1):
        elif 1 and self.playerTies + self.playerLosts > 500:
            # we are nearing the end and we are losing. Play randomly from now on.
            if turnsRemaining > 1 and lostDifference > 1:
                #confidence = (lostDifference) / (turnsRemaining)
                confidence = math.log(lostDifference, turnsRemaining)
                confidence = math.log(lostDifference, totalTurns - lostDifference + (self.playerTies * 1))
            else:
                # this is the last turn and we are still losing. Play randomly.
                confidence = 1
            
            confidence = 1
            
#            print("A: losing at turn", currentTurn)
#            print(self.playerWins, self.playerLosts, self.playerTies)
#            print(lostDifference, confidence)
#            print(turnsRemaining)
#            input()
#        elif 1 and currentTurn > 1 and lostDifference >= self.panicValue:
        elif 0 and turnsRemaining > totalTurns * 0.3  and lostDifference >= self.panicValue:
#        elif currentTurn > (1000 * 0.70) and lostDifference >= self.panicValue:
#        elif currentTurn > (1000 * 0.70) and lostDifference >= self.panicValue:
        
            if lostDifference > 0:       
#               confidence = (lostDifference / self.losingValue)
               confidence = (lostDifference / self.panicValue)
#                confidence = math.log(lostDifference, self.losingValue)
#                confidence = math.log(lostDifference, self.panicValue)

            print("B: losing at turn", currentTurn)
            print(self.playerWins, self.playerLosts, self.playerTies)
            print(lostDifference, confidence)
            print(turnsRemaining)
            input()
        
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0

        self.moveLastTurn = move
        return move, confidence

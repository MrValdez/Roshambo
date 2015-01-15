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
        
        # dna
        #self.losingValue = 100         # if the lost difference reaches this value, the AI is losing 
        self.losingValue = 50           # if the lost difference reaches this value, the AI is losing
        self.panicValue = int(self.losingValue * 0.75) #37  # dna
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
        
        totalTurns = 1000
        currentTurn = rps.getTurn()
        turnsRemaining = totalTurns - currentTurn
        lostDifference = self.playerLosts - self.playerWins
        
        EarlyGame = 20      # DNA   (17-21)

        if currentTurn == 0:
            confidence = 1
        elif currentTurn < EarlyGame:
            # at the beginning of the game, we use our own play since we don't have enough information to predict
            confidence = 1 - (currentTurn / EarlyGame)
#        elif 1 and lostDifference > 1 and currentTurn >= totalTurns - lostDifference + (self.playerTies * 1):
#        elif 1 and self.playerTies + self.playerLosts > 500:
#        elif 1 and currentTurn > 925 and self.playerWins - (self.playerTies + self.playerLosts) < 300:
#        elif 1 and currentTurn > 925 and self.playerWins - self.playerLosts - self.playerTies < 300:
        elif 1 and currentTurn >= 900 and self.playerWins - self.playerLosts <= 50:
            # we are nearing the end and we are losing. Play randomly from now on.           
            if turnsRemaining > 1 and (self.playerLosts - self.playerWins) > 1:
                #confidence = math.log(lostDifference, 50)
                confidence = math.log(lostDifference, turnsRemaining)
                confidence = lostDifference / turnsRemaining
                confidence = lostDifference / 100
            else:
#                this is the last turn and we are still losing. Play randomly.
                confidence = 1
            
#            confidence = 1
            
#            print("A: losing at turn", currentTurn)
#            print(self.playerWins, self.playerLosts, self.playerTies)
#            print(lostDifference, confidence)
#            print(turnsRemaining)
#            input()
            
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0

        self.moveLastTurn = move
        return move, confidence

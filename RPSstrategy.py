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
        
        EarlyGame = 20              # DNA
        LateGame = 1000 * 0.90      # DNA   (last 10%)
        isWinning = (self.playerWins - self.playerLosts) > 50

        if currentTurn == 0:
            confidence = 1
        elif currentTurn < EarlyGame:
            # at the beginning of the game, we use our own play since we don't have enough information to predict
            confidence = 1 - (currentTurn / EarlyGame)
        elif currentTurn >= LateGame and isWinning == False:
            # we are nearing the end and we are losing. Play randomly from now on.           
            x = self.playerLosts - self.playerWins
            
            # make sure confidence stay in range of (0-1)
            if x < -50: x = -50
            if x > +50: x = +50
            
            confidence = math.log((((50 - x) / 100) * 9) + 1, 10)
            
#            print("A: losing at turn", currentTurn)
#            print(self.playerWins, self.playerLosts, self.playerTies)
#            print(lostDifference, confidence)
#            print(turnsRemaining)
#            input()
        else:
            confidence = 0
            
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0

        self.moveLastTurn = move
        return move, confidence

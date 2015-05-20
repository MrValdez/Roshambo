import rps
import math

class RPSstrategy:
    def __init__(self, dna):
        ## todo: move to own class
        ## Strategy Selector
        variant = dna.strategies[0].split(" ")[1:]

        if len (variant) == 0:
            earlygame = 0.02    # 20 turns
            lategame = 1.0 - 0.1      # last 10%
            panicvalue = 50
        else:
            earlygame = float(variant[0])
            lategame = 1.0 - float(variant[1])
            panicvalue = int(variant[2])

        self.EarlyGame = int(1000 * earlygame)
        self.LateGame = int(1000 * lategame)
        self.PanicValue = panicvalue
        ##
        
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
        
        isWinning = (self.playerWins - self.playerLosts) > self.PanicValue

        if currentTurn == 0:
            confidence = 1
        elif currentTurn < self.EarlyGame:
            # at the beginning of the game, we use our own play since we don't have enough information to predict
            confidence = 1 - (currentTurn / self.EarlyGame)
        elif currentTurn >= self.LateGame and isWinning == False:
            # we are nearing the end and we are losing. Play randomly from now on.           
            x = self.playerLosts - self.playerWins
            
            # make sure confidence stay in range of (0-1)
            if x < -self.PanicValue: x = -self.PanicValue
            if x > +self.PanicValue: x = +self.PanicValue
            
            # confidence = math.log((((50 - x) / (100)) * 9) + 1, 10) #original
            confidence = math.log((((self.PanicValue - x) / (self.PanicValue * 2)) * 9) + 1, 10)
            
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

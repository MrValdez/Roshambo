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
        self.moveLastTurn = 0
        
        self.losingValue = 50       # if the lost difference reaches this value, the AI is losing
        self.panicValue = int(self.losingValue * 0.75)
    
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
    
    def play(self):
        move = rps.random() % 3
        confidence = 0
        
        totalTurns = 1000
        currentTurn = rps.getTurn()
        turnsRemaining = totalTurns - currentTurn
        lostDifference = self.playerLosts - self.playerWins
        
        EarlyGame = 20      # DNA
        if currentTurn <= EarlyGame:
            # at the beginning of the game, we use our own play since we don't have enough information
            # to predict
            #if self.playerWins < self.losingValue:
            if currentTurn == 0:
                confidence = 1
            else:
                if EarlyGame > 1:
                    #confidence = currentTurn / EarlyGame
                    confidence = 1 - math.log(currentTurn, EarlyGame)
                        
        if lostDifference >= self.panicValue:
            confidence = (lostDifference / self.losingValue)
            #print(currentTurn, self.playerWins, lostDifference,self.losingValue,confidence)
            #input()
        
        if self.playerLosts + self.playerTies > totalTurns / 3: #dna?
            # Late game
            
            if self.playerWins - self.playerLosts + (turnsRemaining * 2) < self.losingValue:
                # Let's make an assumption that we running out of turns to win
                # If we are going to lose, we might as well play for draws
                confidence = 1
            
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0
        
        return move, confidence

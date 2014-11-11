import rps

class RPSstrategy:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # playerWins and playerLosts refer to the AI's current score and not to this strategy's personal score
        self.playerWins = 0
        self.playerLosts = 0
        self.playerTies = 0
        self.moveLastTurn = 0
        
        self.panicValue = 20
    
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
        if lostDifference > self.panicValue:
            confidence = (lostDifference / self.panicValue) - 1
            #print(lostDifference,confidence)

        
        if self.playerLosts > 200 or self.playerTies > 200:
            # Late game            
            if turnsRemaining + self.playerWins < self.playerLosts * 1.5:
                # Let's make an assumption that we are going to win all of the remaining turns. Will we have enough to win?
                # If we are going to lose, so might as well play for draws
                confidence = 1
            
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0
        
        return move, confidence

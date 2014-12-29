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
        #lostDifference = self.playerLosts + self.playerTies - self.playerWins  # doesn't work
        
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
           
        if currentTurn > 1 and lostDifference >= self.panicValue:
#            print("losing at turn", currentTurn)
#            print(self.playerWins)
#            print(lostDifference)
#            print(turnsRemaining)
#            input()
            if lostDifference < self.losingValue:
                confidence = math.log(lostDifference, self.losingValue)
            else:
                confidence = (lostDifference / self.losingValue)
       
            confidence = (lostDifference / self.losingValue)
            confidence = math.log(lostDifference, self.losingValue)
            #print(currentTurn, self.playerWins, self.playerLosts, lostDifference, confidence)
            #input()
#######        figure out what to do with layer -1
            return move, confidence
        
        # are we in the midgame and are we losing?
        if confidence < 1 and self.playerLosts + self.playerTies > totalTurns / 3: #dna?
        #if turnsRemaining < self.losingValue * 3: #dna?
        #if currentTurn > self.losingValue:        
            # should we panic?
            panicCheck = self.playerWins - self.playerLosts + (turnsRemaining * 2)        ### rank 5/14 (5969)
            #panicCheck = self.playerWins - self.playerLosts + (turnsRemaining * 1.8)      ### rank 5/18 (5781)
            #panicCheck = self.playerWins - self.playerLosts + (turnsRemaining * 2.5)      ### rank 9
            #panicCheck = self.playerWins - self.playerLosts + (turnsRemaining * 1.9)      ### rank 9
            #panicCheck = self.playerWins - self.playerLosts + (turnsRemaining * 2.1)      ### rank 8
            
            #panicCheck = turnsRemaining - lostDifference
                        
            #if panicCheck > self.losingValue:      
            #if lostDifference > self.panicValue:
            #if panicCheck < self.losingValue:      
            
            if self.playerWins < self.playerLosts:
                # Let's make an assumption that we running out of turns to win
                # If we are going to lose, we might as well play for draws
                
                # confidence = (panicCheck / self.losingValue)
                confidence = (lostDifference / (self.losingValue + turnsRemaining))
                #confidence = math.log(lostDifference, self.losingValue + turnsRemaining)
                #print(confidence)
                #confidence = 1
                #print(turnsRemaining, self.playerWins, self.playerLosts, self.playerTies, lostDifference)
                #print("s", panicCheck, self.losingValue)
                #input()
            
        if confidence > 1: confidence = 1
        if confidence < 0: confidence = 0
        
        return move, confidence

import rps
Debug = False
Debug = True

# 1. Evaluate current situation.
#     Situations can exist multiple times but with different moves. 
# 2. Find current situation in database.
#    Ignore situations with low success rate
#    Use different checks to consider if situation is in play
# 3. Rank situations.
# 4. Apply yomi. Choose move based on situation and opponent variables (likelihood of countering, etc).
# 5. Update situation chosen by outcome of turn.
#    Flag this as new for farther training

class Situation:
    def __init__(self, move, situationData):
        self.data = situationData   # the data that describes the current situation
        self.move = move            # the move to play in the given situation
        self.successRate = 0        # goes up or down when the opponent wins or loses
        self.counterPotential = 0   # todo: refers to how likely this will be used as a counter

        #self.enemyRespect          # see onrespect section
    def winCondition(self):
        """ Call this function if the AI wins"""
        self.successRate += 1 # todo: Personality.
    def loseCondition(self):
        """ Call this function if the AI loses"""
        self.successRate -= 1 # todo: Personality.
        
class SituationDB:
    def __init__(self):
        self.Database = []
    def reset(self):
        self.Database.clear()
    def add(self, situation):
        self.Database.append(situation)
    def find(self, perception):
        """ 
        Look into the database for situations that is currently perceived by the system.
        Returns a list of tuples of possible situations. 
        The format for the tuple is: (situation, rank).
        """
        possibleSituations = []
        
        if Debug:
            print ("Current perception on the world: %s" % (perception))
            
        for situation in self.Database:
            # check the last 5 turns
            for i in range(1, 5):
                # find exact matches
                if Debug:
                    print ("Checking situation: %s" % (situation.data))                   
                
                if i >= len(perception) or i >= len(situation.data):
                    break
                
                if len(perception) < i and situation.data == perception[-i:]:
                    rank = 100
                    result = (situation, rank)
                    possibleSituations.append(result)
                
                # matches with just opponent's moves
                if False:                                                           
                    pass
        
        return possibleSituations

class GameHistory:
    def __init__(self):
        #self.history = []
        self.history = ""
    def reset(self):
        #self.history.clear()
        self.history = ""
    def add(self, data):
        #self.history.append(data)
        self.history += str(data)
    def get(self):
        return self.history

def RemoveNoiseInSituation(situationData):
    """ This function removes the noise in the situation. This is dependent on the AI's personality as well as the game.
    Some AI might only look at the last 5 turns. 
    Some games would have extra data that are not helpful or not evaluated in the current situation"""

    # we are only looking at the last 5 turns. Multiplied by 2 to include both the player's and the enemy's moves.
    turns = 5 * 2
    situationData = situationData[-turns:]

    return situationData

def Evaluator(turn):
    global GameHistory
    
    myMove = rps.myHistory(turn)
    data = GameHistory.get()
    data = data[turn:]
    data = RemoveNoiseInSituation(data)
    currentSituationData = data
    
    situation = Situation(myMove, currentSituationData)
    return situation
    
def EvaluateLastTurn():
    previousTurn = rps.getTurn() - 1
    return Evaluator(previousTurn)

def EvaluateThisTurn():
    currentTurn = rps.getTurn()
    return Evaluator(currentTurn)

# global variables
GameHistory = GameHistory()
DB = SituationDB()

def init():
    global GameHistory, DB
    GameHistory.reset()
    DB.reset()
    
def yomi(a):
    #return SkeletonAI()
    #return BeatFrequentPickAI(a)
    
    global Debug
    currentTurn = rps.getTurn()
    move = 0
    
    if currentTurn == 0:
        init()
        
    if currentTurn > 0:
        myMove = rps.myHistory(currentTurn)
        enemyMove = rps.enemyHistory(currentTurn)

        # game has already taken one turn
        # store the situation of the last turn into our database
        # update our game history.        
        global DB
        # store the situation last turn and our move
        perceptionLastTurn = GameHistory.get()
        perceptionLastTurn = RemoveNoiseInSituation(perceptionLastTurn)
        situationLastTurn = Situation(rps.myHistory(currentTurn), perceptionLastTurn)    
        #todo: check if the situation exists already and use that instead
        # update the victory condition 
        if (myMove == 0 and enemyMove == 2) or \
           (myMove == 1 and enemyMove == 0) or \
           (myMove == 2 and enemyMove == 1):
            print ("win")
            situationLastTurn.winCondition()
        else:
            print ("lost")
            situationLastTurn.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
        DB.add(situationLastTurn)  
        if Debug: print ("last turn situation: %s" % (situationLastTurn.data))
        
        global GameHistory
        GameHistory.add(myMove)          # Game history is alternation between ai and enemy moves
        GameHistory.add(enemyMove)       # In other games, game history might be different
        
        if Debug: print ("Current game situation: %s" % (GameHistory.get()))
        
    situation = EvaluateThisTurn()
    possibleSituations = DB.find(situation.data)
    if len(possibleSituations):
        # we find situations in the past that is similar to the current situation.
        pass
    else:
        # we cannot find a situation in the past.
        pass
    
    if Debug: input(">")
    return move

def SkeletonAI():
    """ This is the most basic AI that shows the functions used """
    currentTurn = rps.getTurn()
    
    if currentTurn:
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        
    print ("%i" % (currentTurn))
    print (" %i %i" % (rps.myHistory(currentTurn - 0), rps.enemyHistory(currentTurn - 0)))
    print (" %i %i" % (rps.myHistory(currentTurn - 1), rps.enemyHistory(currentTurn - 1)))
    
    input()
    return (rps.enemyHistory(currentTurn) + 1) % 3
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    return False
    
def BeatFrequentPickAI(a):
    import BeatFrequentPick
    return BeatFrequentPick.move(a)
    
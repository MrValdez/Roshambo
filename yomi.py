import rps
Debug = False
Debug = True

# 1. Evaluate current situation.
#     Situations can exist multiple times but with different moves. 
# 2. Find current situation in database.
#    todo Use different checks to consider if situation is in play
# 3. Rank situations.
# 4. todo Apply yomi. Choose move based on situation and opponent variables (likelihood of countering, etc).
# 5. Update situation chosen by outcome of turn.
#    todo Flag this as new for farther training

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
    def findDuplicate(self, needle):
        """
        Look for an exact duplicate of needle and return the duplicate and True. 
        If no duplicate is found, return the needle and False.
        """
        for situation in self.Database:
            if situation.data == needle.data and    \
               situation.move == needle.move:
               if Debug: print ("Found")
               return situation, True
        return needle, False
    def find(self, perception):
        """ 
        Look into the database for situations that is currently perceived by the system.
        Returns a list of tuples of possible situations. 
        The format for the tuple is: (rank, situation).
        """
        possibleSituations = []
        
        if Debug:
            print ("Current perception on the world: %s" % (perception))
            
        for situation in self.Database:
            situationSize = len(situation.data)
            # check the last 5 turns
            #for i in range(1, 5):
            for i in range(1):
                # find exact matches
                if Debug: print ("Comparing situation in database (move %i): %s" % (situation.move, situation.data))
                
                #if i >= len(perception) or i >= len(situation.data):
                #    break
                
                if situation.data == perception[-situationSize:]:
                    rank = 0
                    if situation.successRate > 0:
                        rank = 100
                    else:
                        rank = -100
                    result = (rank, situation)
                    possibleSituations.append(result)
                    if Debug: print (" ...situation match")
                
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

def EvaluateThisTurn():
    data = GameHistory.get()
    data = RemoveNoiseInSituation(data)
    return data

def experimentNewMove(ClosestFamiliarSituations = None):
    """ 
    This function's purpose is to use a move since either we have seen this situation for the first time
    or our previous options have failed.
    ClosestFamiliarSituations holds either None or a list of tuple of (rank, situation) that may or may not be useful
    in determining what our best move is (for example, if we notice rocks have a slightly higher chance of winning, we try that move)
    This function returns a move. 
    """
    if ClosestFamiliarSituations == None:
        return rps.biased_roshambo (1 / 3.0, 1 / 3.0)       # choose one at random
    
    statR, statP, statS = 0, 0, 0
    total = 0
    for rank, situation in ClosestFamiliarSituations:
        if situation.move == 0: statR += 1
        if situation.move == 1: statP += 1
        if situation.move == 2: statS += 1
        total += 1
    
    return rps.biased_roshambo(statR / float(total), statP / float(total));

def sortRanking(RankingList):
    """
    Sort a ranking list (a tuple of (rank, situation)) with the higher ranking at top.
    Returns the sorted list
    """
    RankingList.sort(key = lambda x: len(x[1].data), reverse=True)     # sort by length of situation (secondary key)
    RankingList.sort(key = lambda x: x[0], reverse=True)     # sort by ranking (primary key)
    
    if Debug: 
        print ("\nRank  Move Situation")
        for foundSituation in RankingList:
            rank, situation = foundSituation
            print ("%s: %s %s" % (str(rank).ljust(4), str(situation.move).ljust(4), situation.data))
    
    return RankingList

# global variables
GameHistory = GameHistory()
DB = SituationDB()

def init():
    global GameHistory, DB
    GameHistory.reset()
    DB.reset()
    
def play(a):
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
        global DB

        # game has already taken at least one turn
        # store the situation of the last turn into our database. Note that we did this before updating the game history, so 
        #  EvaluateThisTurn() still refers to the last turn
        # update our game history.
        # store the situation last turn and our move
        perceptionLastTurn = EvaluateThisTurn()
        situationLastTurn = Situation(myMove, perceptionLastTurn)            
        
        #check if the situation exists already and use that instead
        situationLastTurn, isDuplicate = DB.findDuplicate(situationLastTurn)
        
        # update the victory condition 
        if (myMove == 0 and enemyMove == 2) or \
           (myMove == 1 and enemyMove == 0) or \
           (myMove == 2 and enemyMove == 1):
            situationLastTurn.winCondition()
        else:
            situationLastTurn.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
        if isDuplicate == False:
            DB.add(situationLastTurn)
            if Debug: print ("Saved last turn situation into database: %s move %i" % (situationLastTurn.data, situationLastTurn.move))
        
        global GameHistory
        GameHistory.add(myMove)          # Game history is alternation between ai and enemy moves
        GameHistory.add(enemyMove)       # In other games, game history might be different        
        
    situation = EvaluateThisTurn()
    possibleSituations = DB.find(situation)
    possibleSituations = sortRanking(possibleSituations)
    if len(possibleSituations):
        # we find situations in the past that is similar to the current situation.
        # let's choose using ranking
        
        todo: add code to "forget" low ranking situations
        todo: apply yomi ranking modifier
        todo: one last sort

        # if we are not confident with our plays based on the current situation, we experiment with a new move
        tolerance = 0 #todo: make this a personality
        if possibleSituations[0][0] < tolerance:    #[0][0] refers to the highest ranking tuple, and returns its rank
            move = experimentNewMove(possibleSituations)    # pass all the situations found so we can take them into account (basically, remember what we forgot)
        else:
            move = possibleSituations[0][1].move
    else:
        # we cannot find a situation in the past.
        # so we experiment a new move
        if Debug: print ("new situation encountered")
        move = experimentNewMove(None)
    
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
    global Debug
    return Debug
    
def BeatFrequentPickAI(a):
    import BeatFrequentPick
    return BeatFrequentPick.play(a)
    
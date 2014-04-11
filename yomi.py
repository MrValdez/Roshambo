import rps
Debug = False
Debug = True

# 1. Evaluate current situation.
#     Situations can exist multiple times but with different moves. 
# 2. Find current situation in database.
#    todo Use different checks to consider if situation is in play
# 3. Rank situations.
#    todo Add personality in ranking
# 4. Apply yomi. 
#    todo Choose move based on situation and opponent variables (likelihood of countering, etc).
# 5. Update situation chosen by outcome of turn.
#    todo Flag this as new for farther training

def checkWinner(p1, p2):
    """
    Returns True if p1 wins.
    Returns False if p2 wins.
    Returns None if its a tie
    """
    if p1 == p2:
        return None
        
    if (p1 == 0 and p2 == 2) or \
       (p1 == 1 and p2 == 0) or \
       (p1 == 2 and p2 == 1):
       return True
       
    return False
    
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
    def find(self, currentSituation):
        """ 
        Look into the database for situations that is currently perceived by the system.
        Returns a list of tuples of possible situations. 
        The format for the tuple is: (rank, situation).
        """
        possibleSituations = []
        
        if Debug:
            print ("Current situation of the world: %s" % (currentSituation))
            
        for situation in self.Database:
            situationSize = len(situation.data)
            
            if Debug: print ("Comparing situation in database (move %i): %s" % (situation.move, situation.data))
                        
            # find exact matches
            if situation.data == currentSituation[-situationSize:]:
                if Debug: print (" ...exact situation match")
                
                rank = 0
                if situation.successRate > 0:
                    rank += 100
                else:
                    rank += -100
                result = (rank, situation)
                possibleSituations.append(result)
                continue

            if len(currentSituation) == 0 or len(situation.data) == 0:
                continue

            # find matches where the AI's moves are ignored. 
            # This is to detect opponents that are following a pattern
            matchFound = True
            j = len(situation.data) - 1
            
            for i in range(len(currentSituation) - 1, len(currentSituation) - len(situation.data), -2):
                if currentSituation[i] != situation.data[j]:
                    matchFound = False
                    break
                j -= 2
                
            if matchFound:
                if Debug: print (" ...opponent pattern found")
                
                rank = 0
                if situation.successRate > 0:
                    rank += 100
                else:
                    rank += -100
                result = (rank, situation)
                possibleSituations.append(result)
                continue
                    
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
    if len(RankingList) == 0:
        return RankingList
        
    RankingList.sort(key = lambda x: len(x[1].data), reverse=True)     # sort by length of situation (secondary key)
    RankingList.sort(key = lambda x: x[0], reverse=True)     # sort by ranking (primary key)
    
    if Debug: 
        print ("\nRank  Move Situation")
        for foundSituation in RankingList:
            rank, situation = foundSituation
            print ("%s: %s %s" % (str(rank).ljust(4), str(situation.move).ljust(4), situation.data))
    
    return RankingList

def applyYomi(possibleSituations):
    """
    Read each situation and decide if the AI wants to apply Yomi or not.
    On situations where Yomi is applied, change the situation for the next Yomi layer
    Apply the new situation's rank depending on the AI personality.
    Returns (list of possibleSituations, True if yomi is applied).
    """
    isYomiApplied = False
    return possibleSituations, isYomiApplied

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
        if Debug: input(">")
        
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
        if checkWinner(myMove, enemyMove):
            situationLastTurn.winCondition()
        else:
            situationLastTurn.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
        
        if isDuplicate == False:
            DB.add(situationLastTurn)
            if Debug: print ("Saved last turn situation into database: %s (move %i)" % (situationLastTurn.data, situationLastTurn.move))
        
        #create situation from opponent's POV
        situationOpponentPOV = Situation(enemyMove, perceptionLastTurn)
        situationLastTurn, isDuplicate = DB.findDuplicate(situationOpponentPOV)
        if checkWinner(myMove, enemyMove):
            situationOpponentPOV.winCondition()
            # the opponent won with this move, so we increase the next layer's counter potential 
            # (we are anticipating that the enemy will use this again)
            #situationOpponentPOV.successRate += -20 # todo: turn this into a personality variable: respect. todo: mark this as something to train against
        else:
            situationOpponentPOV.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
            # the opponent lost with this move, so we decrease the next layer's counter potential 
            # (we are anticipating that the enemy will not use this again)
            #situationOpponentPOV.successRate += 20 # todo: turn this into a personality variable: disrespect. todo: mark this as something to train against
        if isDuplicate == False:    
            DB.add(situationOpponentPOV)
            if Debug: print ("Saved last turn situation from opponent's point of view: %s (move %i)" % (situationOpponentPOV.data, situationOpponentPOV.move))
            
        if Debug: print("----\n")
        
        global GameHistory
        GameHistory.add(myMove)          # Game history is alternation between ai and enemy moves
        GameHistory.add(enemyMove)       # In other games, game history might be different        
        
    situation = EvaluateThisTurn()
    possibleSituations = DB.find(situation)
    possibleSituations = sortRanking(possibleSituations)
    if len(possibleSituations):
        # we've found situations in the past that is similar to the current situation.
        # let's choose using ranking
        possibleSituations, isYomiApplied = applyYomi(possibleSituations)
        
        if isYomiApplied:
            # one last sort after yomi changes
            if Debug: print ("Resorting because of Yomi changes")
            
            possibleSituations = sortRanking(possibleSituations)
            

        # if we are not confident with our plays based on the current situation, we experiment with a new move
        tolerance = 0 #todo: make this a personality
        if possibleSituations[0][0] < tolerance:            # [0][0] refers to the highest ranking tuple, and returns its rank
            move = experimentNewMove(possibleSituations)    # pass all the situations found so we can take them into account (basically, remember what we forgot)
        else:
            move = possibleSituations[0][1].move
    else:
        # we cannot find a situation in the past.
        # so we experiment a new move
        if Debug: print ("new situation encountered")
        move = experimentNewMove(None)
    
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
    
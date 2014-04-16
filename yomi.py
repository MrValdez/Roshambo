import rps
Debug = True
Debug = False

possible yomi: create the situations at the start of the game where it looks at all the options of the opponent. (game counter analysis)
inspiration: pokemon gives you an idea on the pokeman list.
	

    Here is a better example using m, C1, C2, and C3.

    I have my CB Salamence. It's pretty powerful, it KOs a lot of stuff. But you can counter my m, CB Salamence, with your C1, Skarmory. However, I am prepared for this. I have C2, Magneton. However, what if you have a C3, a Dugtrio? I now have the option of using m and predicting Dugtrio or predicting Skarmory and using C2.

    By using m to counter Dugtrio, C3, it is in effect C4, but since it's main function is m, it won't really be considered C4. It's like closing a box by putting each edge over the edge just to the left of it, including the 4th edge over the first one. In this way each edge (or layer) covers (or counters) another one. 

           

# current todo: add yomi layers to situations

# 1. Evaluate current situation.
#     Situations can exist multiple times but with different moves. 
# 2. Find current situation in database.
#     Use different checks to consider if situation is in play.
#    todo Each check has different ranking depending on the AI's personality
# 3. Rank situations.
#    todo Add personality to ranking (preferences)
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

        #self.enemyRespect          # todo: see onrespect section
        
        self.nextYomiLayer = []
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
        #print(len(self.Database))
    def findDuplicate(self, needle):
        """
        Look for an exact duplicate of needle and return the duplicate and True. 
        If no duplicate is found, return the needle and False.
        """
        for situation in self.Database:
            if situation.data == needle.data and    \
               situation.move == needle.move:
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
            print ("Current situation of the world:           %s\n" % (currentSituation))
            
        for situation in self.Database:
            situationSize = len(situation.data)
            
            if Debug: print ("Comparing situation in database: (move %i) %s" % (situation.move, situation.data))
            
            if situation.data.find("?") == -1:
                if self._findExactMatch(currentSituation, situation.data):
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

                if self._findPatternMatch(currentSituation, situation.data):
                    if Debug: print (" ...opponent pattern found")
                    
                    rank = 0
                    if situation.successRate > 0:
                        rank += 100
                    else:
                        rank += -100
                    result = (rank, situation)
                    possibleSituations.append(result)
                    continue
            else:
                # the situation has a wildcard. So we see if we have anything in the database that fits the wildcards
                if len(currentSituation) == 0:
                    # when checking with a wildcard, make sure that the situation is not empty (neutral situation)
                    continue
                    
                if self._findWildcardMatch(currentSituation, situation.data):
                    if Debug: print (" ...exact situation match with wildcard")
                    
                    rank = 0
                    if situation.successRate > 0:
                        rank += 100
                    else:
                        rank += -100
                    result = (rank, situation)
                    possibleSituations.append(result)
                    continue

                if len(situation.data) == 0:
                    continue

                if self._findPatternMatch(currentSituation, situation.data):
                    if Debug: print (" ...opponent pattern found with wildcard")
                    
                    rank = 0
                    if situation.successRate > 0:
                        rank += 100
                    else:
                        rank += -100
                    result = (rank, situation)
                    possibleSituations.append(result)
                    continue                    
        return possibleSituations
    def _findExactMatch(self, currentSituation, situationData):
        # find exact matches
        lenSituationData = len(situationData)
        if lenSituationData % 2 == 0:
            # even lengths means its not a counter move
            if situationData == currentSituation[-lenSituationData:]:
                return True
        else:
            if situationData == currentSituation[-(lenSituationData + 1):-1]:
                return True
        return False
    def _findWildcardMatch(self, currentSituation, situationData):
        # find exact matches
        i = 0
        for s in currentSituation[-len(situationData):]:
            if situationData[i] != "?" and s != situationData[i]:
                return False
            i += 1
        return True
    def _findPatternMatch(self, currentSituation, situationData):
        # find matches where the AI's moves are ignored. 
        # This is to detect opponents that are following a pattern
        situationDataSize = len(situationData)
        currentSituationSize = len(currentSituation)
        if currentSituationSize < situationDataSize:
            return False
        
        matchFound = True
        j = situationDataSize - 1
        for i in range(currentSituationSize - 1, currentSituationSize - situationDataSize, -2):
            if currentSituation[i] != situationData[j]:
                matchFound = False
                break
            j -= 2
            
        return matchFound
        
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

def saveSituationLastTurn():
    """
    This is called after each players chooses a move and before updating the current turn's situation.
    Evaluate the last turn and the moves played. 
    If there's duplicate, use that. Else, add the new situation to the database
    Do this for the player and the opponent
    """
    global DB
    currentTurn = rps.getTurn()
    myMove = rps.myHistory(currentTurn)
    enemyMove = rps.enemyHistory(currentTurn)

    perceptionLastTurn = EvaluateThisTurn()
    
    # create situation from AI's POV
    situationLastTurn = Situation(myMove, perceptionLastTurn)
    
    # check if the situation exists already and use that instead
    situationLastTurn, isDuplicate = DB.findDuplicate(situationLastTurn)
    
    # update the victory condition 
    if checkWinner(myMove, enemyMove):
        situationLastTurn.winCondition()
    else:
        situationLastTurn.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
    
    if isDuplicate == False:
        DB.add(situationLastTurn)
        if Debug: print ("Saved last turn situation into database: %s (move %i)" % (situationLastTurn.data, situationLastTurn.move))
        createYomiLayers(situationLastTurn)
    
    # create situation from opponent's POV (same sequence as above except we also increase its counter rate
    situationOpponentPOV = Situation(enemyMove, perceptionLastTurn)
    situationOpponentPOV, isDuplicate = DB.findDuplicate(situationOpponentPOV)
 
    if checkWinner(enemyMove, myMove):
        situationOpponentPOV.winCondition()
        # the opponent won with this move, so we increase the next layer's counter potential 
        # (we are anticipating that the enemy will use this again)
        situationOpponentPOV.counterPotential += 20 # todo: turn this into a personality variable: respect. todo: mark this as something to train against
    else:
        situationOpponentPOV.loseCondition()   #todo: is it a good idea to have ties as a losing condition?        
        # the opponent lost with this move, so we decrease the next layer's counter potential 
        # (we are anticipating that the enemy will not use this again)
        situationOpponentPOV.counterPotential += -20 # todo: turn this into a personality variable: disrespect. todo: mark this as something to train against
     
    if isDuplicate == False:    
        DB.add(situationOpponentPOV)
        if Debug: print ("Saved last turn situation from opponent's point of view: %s (move %i)" % (situationOpponentPOV.data, situationOpponentPOV.move))
        createYomiLayers(situationOpponentPOV)
            
def RemoveNoiseInSituation(situationData):
    """ This function removes the noise in the situation. This is dependent on the AI's personality as well as the game.
    Some AI might only look at the last 5 turns. 
    Some games would have extra data that are not helpful or not evaluated in the current situation"""

    # we are only looking at the last 5 turns. Multiplied by 2 to include both the player's and the enemy's moves.
    # todo: make this into a personality
    turns = 5 * 2
    turns = 2 * 2
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
        
    RankingList.sort(key = lambda x: x[0], reverse=True)     # sort by ranking (primary key)
    
    if Debug: 
        print ("\nRank  Move Win Counter Situation")
        for foundSituation in RankingList:
            rank, situation = foundSituation
            rank = str(rank).rjust(4)
            move = str(situation.move).rjust(2) + " "
            win = str(situation.successRate).rjust(3) + " "
            counter = str(situation.counterPotential).rjust(6) + " "
            print ("%s: %s %s %s %s" % (rank, move, win, counter, situation.data))
    
    return RankingList

def findCounter(move):
    return (move + 1) % 3

def createYomiLayers(yomi0):
    def createOneLayer(situation, layerNumber):
        newSituationData = situation.data + str(situation.move)     # The new situation is that there is a prediction from the opponent that we are playing the situation in our database.
        nextYomiLayer = Situation(findCounter(situation.move), newSituationData)

        nextYomiLayer, isDuplicate = DB.findDuplicate(nextYomiLayer)
        
        if isDuplicate == False:    
            # add the new yomi prediction if it doesn't exist
            situation.nextYomiLayer.append(nextYomiLayer)
            DB.add(nextYomiLayer)
            if Debug: print ("Saved yomi layer %i: %s (move %i)" % (layerNumber, nextYomiLayer.data, nextYomiLayer.move))
        return nextYomiLayer

    yomi1 = createOneLayer(yomi0, 1)
    yomi2 = createOneLayer(yomi1, 2)
    yomi3 = createOneLayer(yomi2, 3)
    yomi3.nextYomiLayer.append(yomi0)
    
    yomi1.counterPotential += -20 #todo personality
    yomi2.counterPotential += -10 #todo personality
    yomi3.counterPotential += -0 #todo personality

def applyYomi(possibleSituations):
    """
    Read each situation and decide if the AI wants to apply Yomi or not.
    On situations where Yomi is applied, change the situation for the next Yomi layer
    Apply the new situation's rank depending on the AI personality.
    Returns (list of possibleSituations, True if yomi is applied).
    """
    isYomiApplied = False
    
    for rank, situation in possibleSituations:
        tolerance = 0   # tolerance refers to how likely the AI is going to use a counter. todo: should be a personality
        if situation.counterPotential > tolerance:
            if Debug: print("Apply yomi layer %i to situation %s. New move is %i" % (-1, situation.data, (situation.move + 1) % 3))
            nextYomiLayer = situation.nextYomiLayer[0]
            newRank = 1000 # todo: modified by personality
            possibleSituations.append((newRank, nextYomiLayer))
            isYomiApplied = True
        
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
                
        # game has already taken at least one turn
        # store the situation of the last turn into our database. Note that we did this before updating the game history, so 
        #  when calling EvaluateThisTurn() in the UpdateDatabase(), it still refers to the last turn
        saveSituationLastTurn()

        if Debug: print("----\n")
        
        # update the game history and situation        
        global GameHistory
        myMove = rps.myHistory(currentTurn)
        enemyMove = rps.enemyHistory(currentTurn)
        
        GameHistory.add(myMove)          # Game history is alternation between ai and enemy moves
        GameHistory.add(enemyMove)       # In other games, game history might be different        
        
    situation = EvaluateThisTurn()
    possibleSituations = DB.find(situation)
    if len(possibleSituations):
        # we've found situations in the past that is similar to the current situation.
        # let's choose using ranking
        possibleSituations = sortRanking(possibleSituations)
        possibleSituations, isYomiApplied = applyYomi(possibleSituations)
        
        if isYomiApplied:
            # one last sort after yomi changes
            if Debug: print ("Re-sorting because of Yomi changes")
            
            possibleSituations = sortRanking(possibleSituations)
            
        highestRanking = possibleSituations[0]              # highestRanking is a tuple that contains (ranking, situation class)
        
        # if we are not confident with our plays based on the current situation, we experiment with a new move
        tolerance = 0 #todo: make this a personality
        if highestRanking[0] < tolerance:
            move = experimentNewMove(possibleSituations)    # pass all the situations found so we can take them into account when experimenting
        else:
            move = highestRanking[1].move
    else:
        # we cannot find a situation in the past.
        # so we experiment a new move
        move = experimentNewMove(None)
        
        if Debug: print ("new situation encountered")
    
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
    
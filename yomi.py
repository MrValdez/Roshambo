import rps
Debug = True
Debug = False

MemorySize = 4

class MemorySource:
    """
    This class contains a set of boolean that declares where a memory was found
    """
    def __init__(self, FullSituation = False, AISituation = False, EnemySituation = False):
        self.FullSituation   = FullSituation
        self.AISituation = AISituation 
        self.EnemySituation  = EnemySituation
        
        if not (FullSituation or AISituation or EnemySituation):
            raise "Memory fragment incomplete"

class MemoryFragment:
    """ 
    This is a struct that holds the data for a memory fragment.
    prediction is our prediction on what will happen in the future as our memory tells us
    memoryPosition holds where in memory the fragment can be found
    a set of boolean that declares where a specific memory was found
    """
    def __init__(self, prediction, memoryPosition, memorySource):
        if type(prediction) == str:
            raise 'prediction should be type int'
        self.prediction      = prediction
        self.memoryPosition  = memoryPosition
        self.memorySource    = memorySource

class SituationDB:
    def __init__(self):
        self.reset()
    def reset(self):
        self.FullSituation  = ""   # holds the player's and enemy's moves
        self.AISituation    = ""   # just the player's moves
        self.EnemySituation = ""   # just the enemy's moves
    def add(self, myMove, enemyMove):
        myMove = str(myMove)
        enemyMove = str(enemyMove)
        
        self.FullSituation  += myMove + enemyMove
        self.AISituation    += myMove
        self.EnemySituation += enemyMove
    def guessMove(self):
        rock = 1 / 3.0
        paper = 1 / 3.0
        guess = rps.biased_roshambo (rock, paper)       # choose one at random
        
        return MemoryFragment(prediction = guess,
                               memoryPosition = None,
                               memorySource = None)
    def predict(self, currentTurn):
        """
        returns a list of memory fragments where we "remember" in our memory the current situation.
        if we don't have a memory of the current situation, guess.
        """        
        def searchDB(DB):
            """ returns a list of index where we receive a memory hit """
            # get the last n turns where n is our memory size
            n = MemorySize
            dbSize = len(DB)
            if n > dbSize:
                n = dbSize
            memoryFragment = DB[-n:]
            
            hits = []
            found = dbSize - n
            while True:
                found = DB.rfind(memoryFragment, 0, found)
                if found == -1:
                    break
                hits.append(found)
            return hits
        
        def CreatePredictions(DB):
            predictions = []
            
            hitList = searchDB(DB)
            if not (hitList == None or len(hitList) == 0):
                for hit in hitList:
                    if DB == self.FullSituation:
                        offset = 2
                    else:
                        offset = 1
                    
                    if DB == self.FullSituation:
                        memorySource = MemorySource(FullSituation = True)
                    elif DB == self.EnemySituation:
                        memorySource = MemorySource(EnemySituation = True)
                    elif DB == self.AISituation:
                        memorySource = MemorySource(AISituation = True)
                        
                    predictMove = DB[hit + offset]
                    predictMove = int(predictMove)

                    memory = MemoryFragment(prediction = predictMove,
                                            memoryPosition = hit,
                                            memorySource = memorySource)
                    predictions.append(memory)
        
            return predictions
        
        if currentTurn == 0:
            return [self.guessMove()]
        
        memoryFragments = []
        #memoryFragments.extend(CreatePredictions(self.FullSituation))
        #memoryFragments.extend(CreatePredictions(self.AISituation))
        memoryFragments.extend(CreatePredictions(self.EnemySituation))
        
        if len(memoryFragments) == 0:
            return [self.guessMove()]
            
        return memoryFragments
        
def applyYomi(memoryFragments):
    finalMove = 0
    for memory in memoryFragments:
        move = memory.prediction
        yomiLayer1 = (move + 1) % 3
        yomiLayer2 = (move + 2) % 3
        yomiLayer3 = (move + 3) % 3
        finalMove = yomiLayer1
    return finalMove
                
situationDB = SituationDB()
def init():
    situationDB.reset()
    
def play(a):
    global situationDB
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init()
    else:
        # record the last turn
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        situationDB.add(myMoveLastTurn, enemyMoveLastTurn)

    memoryFragments = situationDB.predict(currentTurn)
    move = applyYomi(memoryFragments)
    
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
    
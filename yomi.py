import BeatFrequentPick
import rps
Debug = True
Debug = False

# todo: values to experiment on:
MemorySize = 4
MemoryFragmentLimit = 3         # how many memories we need to remember

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

class MemoryFragment:
    """ 
    This is a struct that holds the data for a memory fragment.
    prediction is our prediction on what will happen in the future as our memory tells us
    memoryPosition holds where in memory the fragment can be found
    confidence tells how confident we are with the memory
    """
    def __init__(self, prediction, memoryPosition, confidence):
        if type(prediction) == str:
            raise 'prediction should be type int'
        self.prediction      = prediction
        self.memoryPosition  = memoryPosition
        self.confidence      = confidence

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
        confidence = 0  #todo: personality
        
        return MemoryFragment(prediction = guess,
                               memoryPosition = None,
                               confidence = confidence)
    def predict(self, currentTurn):
        """
        returns a list of memory fragments where we "remember" in our memory the current situation.
        if we don't have a memory of the current situation, guess.
        """        
        def searchDB(DB):
            """ returns a list of index where we receive a memory hit """
            # get the last n turns where n is our memory size
            global MemorySize, MemoryFragmentLimit
            
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
                if len(hits) >= MemoryFragmentLimit:
                    break
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
                    
                    # todo: confidence should depend on a heuristics
                    confidence = 0
                    if DB == self.FullSituation:
                        confidence = 100
                    elif DB == self.EnemySituation:
                        confidence = 80
                    elif DB == self.AISituation:
                        confidence = 80
                        
                    predictMove = DB[hit + offset]
                    predictMove = int(predictMove)

                    memory = MemoryFragment(prediction = predictMove,
                                            memoryPosition = hit,
                                            confidence = confidence)
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

class Yomi():
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.enemyYomiTendencies = [0, 0, 0]            # Prefered move, first yomi layer, second yomi layer, 
        
        # These are data from the last turn
        self.prevPredictedEnemyMove = 0                 # This holds the move we've predicted the enemy will use
        self.prevPredictedEnemyYomiLayer = 0 
        self.prevAIYomiLayer = 0
        
    def update(self, myMoveLastTurn, enemyMoveLastTurn):
         # decay the yomi layers
         #for i in range(len(self.enemyYomiTendencies)):
         #   self.enemyYomiTendencies[i] -= 0.1
            
         def updateEnemyYomiTendencies(layer, positiveModification = 1, negativeModification = -1):
            if Debug: print("updating enemy's layer from last turn: ", layer)
            for i in range(len(self.enemyYomiTendencies)):
                if i == layer:
                    self.enemyYomiTendencies[i] += positiveModification
                else:
                    self.enemyYomiTendencies[i] += negativeModification            
         
         def findMoveYomiLayer(move, predictedMove, predictedLayer):
            """ returns the layer that move can be found based on the move we predicted will be used """
            layer = predictedLayer
            while True:
                if move == predictedMove:
                    return layer
                move -= 2
                if move < 0:
                    move += 3
                    move = move % 3
                    layer -= 1
                    if layer < 0:
                        layer = len(self.enemyYomiTendencies) - 1
         
         if myMoveLastTurn == enemyMoveLastTurn:
            # its a tie
            updateEnemyYomiTendencies(self.prevAIYomiLayer, positiveModification = -0.5, negativeModification = 0)   #todo: personality
         else:
            currentEnemyLayer = findMoveYomiLayer(enemyMoveLastTurn, self.prevPredictedEnemyMove, self.prevPredictedEnemyYomiLayer)
            #AIwins = checkWinner(myMoveLastTurn, enemyMoveLastTurn)
            #if AIWins:
            #else:
            updateEnemyYomiTendencies(currentEnemyLayer)   #todo: personality

            
    def _chooseEnemyYomiLayer(self):
        expectedEnemyYomiLayer = None
        
        # check for highest tendencies
        maxValue = max(self.enemyYomiTendencies)
        count = self.enemyYomiTendencies.count(maxValue)

        if count == 1:
            # one yomi layer has the highest tendency. Get that layer
            for i, val in enumerate(self.enemyYomiTendencies):
                if maxValue == val:
                    expectedEnemyYomiLayer = i
        else:
            # multiple yomi layers has the same value. Let's choose randomly between them.
            maxValue = max(self.enemyYomiTendencies)
            count = self.enemyYomiTendencies.count(maxValue)
            choice = rps.random() % count
            
            for i, val in enumerate(self.enemyYomiTendencies):
                if val == maxValue:
                    if choice == 0:
                        expectedEnemyYomiLayer = i
                        
                        break
                    choice -= 1            
            if Debug: print ("Choosing at random. \nenemy's predicted layer: ", expectedEnemyYomiLayer)
            
        if expectedEnemyYomiLayer == None: #shouldn't happen
            return 0      # default. We can't read the enemy's current yomi, so let's play safe and use layer 0 (todo: should use personal favorite)
        
        self.prevPredictedEnemyYomiLayer = expectedEnemyYomiLayer
        
        AIYomiLayer = (expectedEnemyYomiLayer + 1) % 3 # play at a higher layer. todo: we don't always want to do this.
        self.prevAIYomiLayer = AIYomiLayer
        
        return AIYomiLayer
            
    def _getYomiLayerMove(self, move, layer):
        # returns the move at yomi layer
        return (move + (layer + 1)) % 3
        
    def applyYomi(self, memoryFragments):
        enemyMove = 0
        # select the move that we think the opponent favors
        enemyMove = memoryFragments[0].prediction
        self.prevPredictedEnemyMove = enemyMove
        if Debug: print("predicting that enemy will use", enemyMove)
        
        # check if we should use yomi on the current prediction
        enemyLayer = self._chooseEnemyYomiLayer()
        if Debug: 
            print(self.enemyYomiTendencies)
            print("playing with yomi ", enemyLayer) 
            input()
        enemyMove = self._getYomiLayerMove(enemyMove, enemyLayer)
        
        return enemyMove

def predict(a):
    """ returns a list of memoryFragments that we think the opponet will choose """

    currentTurn = rps.getTurn()
    memoryFragments = situationDB.predict(currentTurn)
    
    bfpMove = BeatFrequentPick.play(a)
    bfpFragment = MemoryFragment(prediction = bfpMove,
                                 memoryPosition = None,
                                 confidence = 100)

    memoryFragments.append(bfpFragment)
    memoryFragments.sort(key = lambda x : x.confidence, reverse = True)
    return memoryFragments
    

yomi = Yomi()                
situationDB = SituationDB()
def init():
    situationDB.reset()
    yomi.reset()
    
def play(a):
#    return BeatFrequentPick.play(a)
    global situationDB
    global enemyPersonality, playerPersonality
    currentTurn = rps.getTurn()
    
    if Debug: print("\n")
    
    if currentTurn == 0:
        init()
    else:
        # record the last turn
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        situationDB.add(myMoveLastTurn, enemyMoveLastTurn)
        
        yomi.update(myMoveLastTurn, enemyMoveLastTurn)
        
    memoryFragments = predict(a)
    move = yomi.applyYomi(memoryFragments)
    
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
    
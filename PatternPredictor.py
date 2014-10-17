import rps

Debug = True
Debug = False
    
enemyHistory = ""
windowSize = None

def play(a):           
    global enemyHistory
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        init(a)
        return 0, 0         # play Rock with 0 confidence
        
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)
    enemyHistory += str(enemyMoveLastTurn)
    History = enemyHistory
    
    for SequenceLength in windowSize:
        if SequenceLength > currentTurn:
            # our window is bigger than the history size, so we ignore this window length
            continue
            
        prediction, confidence = CheckHistory(History, SequenceLength)
        if prediction != -1:
            return prediction, confidence
            
    # no Seq found.
    return 0, 0         # play Rock with 0 confidence

def init(a):
    global windowSize
    global enemyHistory

    enemyHistory = ""

    if windowSize == None:
        if a == -1:
            # default windowSize
            a = [1, 2, 3, 4, 5]
            a.sort(reverse=True)
        else:
            a = str(a).split(",")
            a = [int(turn) for turn in a]
            a.sort(reverse=True)
            
        windowSize = a        

def CheckHistory(History, SequenceLength):
    """return prediction, confidence"""

    Seq = History[-SequenceLength:]
    found = History.find(Seq, 0, -SequenceLength)
    if found == -1:
        return -1, -1

    # list how many times we see a predicted move
    tally = [0, 0, 0]      # [0] = rock, [1] = paper, [2] = scissor
    while found != -1:
        end = found + len(Seq)
        move = History[end:end + 1]
        move = int(move)

        tally[move] += 1
        found = History.find(Seq, found + 1, -SequenceLength)
 
    prediction, confidence = GetHighestTally(History, tally, SequenceLength)

    if Debug:
        currentTurn = rps.getTurn()
        print ("Sequence to look for:          ", Seq)
        print ("Position of latest found Seq:  ", History.rfind(Seq, 0, currentTurn - 1))
        print ("Predicted move:                ", prediction)
        print ("Confidence:                    ", confidence)
        input()

    return prediction, confidence
 
def GetHighestTally(History, tally, SequenceLength):            
    # check if we have a tie for maximum.
    maxCount = max(tally)
    numCount = tally.count(maxCount)

    if numCount == 1:
        # we don't have a tie for maximum. Get the highest move
        confidence = 1.0
        for i, count in enumerate(tally):
            if count == maxCount:
                prediction = i
                return prediction, confidence                            

    # we have a tie.
    # let's see what move was played the most in the entire History
    moveCounts = [0, 0, 0]
    if tally[0] == maxCount: moveCounts[0] = History.count("0")
    if tally[1] == maxCount: moveCounts[1] = History.count("1")
    if tally[2] == maxCount: moveCounts[2] = History.count("2")
    
    prediction = -1
    moveCountMax = max(moveCounts)
    moveCountNum = moveCounts.count(moveCountMax)
    if moveCountNum == 1:
        confidence = 1.0
        prediction = moveCounts.index(moveCountMax)
        return prediction, confidence

    # if we still have a tie, choose between them using a random number
    sumCount = maxCount * numCount
    
    for i, count in enumerate(tally):
        if count == maxCount:
            tally[i] = count / sumCount
        else:
            tally[i] = 0
    
    random = rps.randomRange()
        
    for i, randomNumber in enumerate(tally):
        if random <= randomNumber:
            prediction = i
            break
        random -= randomNumber

    if prediction == -1:
        return -1, 0

    confidence = tally[prediction]
                            
    return prediction, confidence
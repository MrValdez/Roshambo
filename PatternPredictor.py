import rps

Debug = True
Debug = False
    
enemyHistory = ""
windowSize = None

def play(a):
    init(a)
           
    global enemyHistory
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        enemyHistory = ""
        return 0, 0         # play Rock with 0 confidence
        
    # myMoveLastTurn = rps.myHistory(currentTurn)
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)

    enemyHistory += str(enemyMoveLastTurn)
    history = enemyHistory
    
    for windowLength in windowSize:
        if windowLength > currentTurn:
            # our window is bigger than the history size, so we ignore this window length
            continue
            
        prediction, confidence = CheckHistory(history, windowLength)
        if prediction != -1:
            return prediction, confidence
            
    # no seq found.
    return 0, 0         # play Rock with 0 confidence

def init(a):
    global windowSize
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

def CheckHistory(history, windowLength):
    """return prediction, confidence"""

    seq = history[-windowLength:]
    found = history.find(seq, 0, -windowLength)
    if found == -1:
        return -1, -1

    # list how many times we see a predicted move
    tally = [0, 0, 0]      # [0] = rock, [1] = paper, [2] = scissor
    while found != -1:
        end = found + len(seq)
        move = history[end:end + 1]
        move = int(move)

        tally[move] += 1
        found = history.find(seq, found + 1, -windowLength)
 
    prediction, confidence = GetHighestTally(history, tally, windowLength)

    if Debug:
        currentTurn = rps.getTurn()
        print ("Sequence to look for:          ", seq)
        print ("Position of latest found seq:  ", history.rfind(seq, 0, currentTurn - 1))
        print ("Predicted move:                ", prediction)
        print ("Confidence:                    ", confidence)
        input()

    return prediction, confidence
 
def GetHighestTally(history, tally, windowLength):            
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
    # let's see what move was played the most in the entire history
    moveCounts = [0, 0, 0]
    if tally[0] == maxCount: moveCounts[0] = history.count("0")
    if tally[1] == maxCount: moveCounts[1] = history.count("1")
    if tally[2] == maxCount: moveCounts[2] = history.count("2")
    
    prediction = -1
    moveCountMax = max(moveCounts)
    moveCountNum = moveCounts.count(moveCountMax)
    if moveCountNum == 1:
        confidence = 1.0
        for i, count in enumerate(moveCounts):
            if count == moveCountMax:
                prediction = i
                break    
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
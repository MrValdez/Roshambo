import rps

Debug = True
Debug = False
    
enemyHistory = ""
windowSize = None

def play(a):
    global windowSize
    if windowSize == None:
        if a == -1:
            a = [1, 2, 3, 4, 5]
            a.sort(reverse=True)
        else:
            a = str(a).split(",")
            a = [int(turn) for turn in a]
            a.sort(reverse=True)
            
        windowSize = a        
           
    global enemyHistory
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        enemyHistory = ""
        return 1, 0         # play Rock with 0 confidence
        
    # myMoveLastTurn = rps.myHistory(currentTurn)
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)

    enemyHistory += str(enemyMoveLastTurn)
    history = enemyHistory
    
    bestMove = 0
    bestConfidence = -1
    for i, windowLength in enumerate(windowSize):
        if windowLength > currentTurn:
            # our window is bigger than the history size, so we ignore this window length
            continue
            
        seq = history[-windowLength:]
        found = history.find(seq, 0, -windowLength)
                
        if found == -1:
            continue
        else:
            # list how many times we see a predicted move
            possiblePredictions = [0, 0, 0]      # [0] = rock, [1] = paper, [2] = scissor
            while found != -1:
                end = found + len(seq)
                move = history[end:end + 1]
                move = int(move)

                possiblePredictions[move] += 1
                found = history.find(seq, found + 1, -windowLength)
                    
            # check if we have a tie for maximum.
            maxCount = max(possiblePredictions)
            numCount = possiblePredictions.count(maxCount)

            if numCount == 1:
                # we don't have a tie for maximum. Get the highest move
                for i, count in enumerate(possiblePredictions):
                    if count == maxCount:
                        move = i
                        return move, 1.0
                             
                confidenceInSequenceFound = 1.0
            else:
                # we have a tie.
                # let's see if what move has the most in the entire history
                moveCounts = [0, 0, 0]
                if possiblePredictions[0] == maxCount: moveCounts[0] = history.count("0")
                if possiblePredictions[1] == maxCount: moveCounts[1] = history.count("1")
                if possiblePredictions[2] == maxCount: moveCounts[2] = history.count("2")
                
                moveCountMax = max(moveCounts)
                moveCountNum = moveCounts.count(moveCountMax)
                if moveCountNum == 1:
                    for i, count in enumerate(moveCounts):
                        if count == moveCountMax:
                            move = i
                            break                
                    confidenceInSequenceFound = 1.0
                else:                
                    # if we still have a tie, choose between them using a random number
                    sumCount = maxCount * numCount
                    for i, count in enumerate(possiblePredictions):
                        if count == maxCount:
                            possiblePredictions[i] = count / sumCount
                        else:
                            possiblePredictions[i] = 0
                            
                    random = rps.randomRange()               
                        
                    for i, randomNumber in enumerate(possiblePredictions):
                        if random <= randomNumber:
                            move = i
                            break
                        random -= randomNumber

                    confidenceInSequenceFound = possiblePredictions[move]

            if len(history) - windowLength < 0:
                confidenceInSequence = (i + 1) / windowLength
            else:
                confidenceInSequence = (i + 1) / len(windowSize)
            confidence = (confidenceInSequence * 0.75) + (confidenceInSequenceFound * 0.25)
                                
            if bestConfidence < confidence:
                if Debug:
                    print ("Sequence to look for:          ", seq)
                    print ("Position of latest found seq:  ", history.rfind(seq, 0, currentTurn - 1))
                    print ("Predicted move:                ", move)
                    print ("Confidence:                    ", confidence)

                if Debug and bestConfidence != -1:
                    print ("confidence changed from %.2f to %.2f" % (bestConfidence, confidence))
                    
                bestConfidence = confidence 
                bestMove = move              
                
            return move, confidence         # uncomment this to check all the sequences

    if Debug and bestConfidence >= 0:
        print ("Current history:               ", history)
        print ("Enemy move predicted:          ", bestMove)
        print ("Confidence:                    ", bestConfidence)
        input()
            
    return bestMove, bestConfidence
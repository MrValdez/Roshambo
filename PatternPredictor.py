import rps

Debug = True
Debug = False
    
enemyHistory = ""
turnsToCheck = [1, 2, 3, 4, 5, 10, 15, 20, 25, 50]
turnsToCheck.reverse()

def play(a):
    global enemyHistory
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        enemyHistory = ""
        return 1, 0
        return rps.biased_roshambo (1/3.0, 1/3.0), 0
        
    myMoveLastTurn = rps.myHistory(currentTurn)
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)

    enemyHistory += str(enemyMoveLastTurn)
    history = enemyHistory
    
    bestMove = 0
    bestConfidence = -1
    for i, turn in enumerate(turnsToCheck):
        if turn > currentTurn:
            continue
            
        seq = history[-turn:]
        #found = history.rfind(seq, 0, currentTurn - 1)
        found = history.rfind(seq, 0, -turn)
                
        if found != -1:
            # list how many times we see a predicted move
            possiblePredictions = [0, 0, 0]      # [0] = rock, [1] = paper, [2] = scissoros
            while found != -1:
                end = found + len(seq)
                move = history[end:end + 1]
                move = int(move)

                possiblePredictions[move] += 1
                found = history.rfind(seq, 0, found)
                    
            maxCount = max(possiblePredictions)
            # check if we have a tie for maximum. if we do, choose between them using a random number
            numCount = possiblePredictions.count(maxCount)
            if numCount > 1:
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
            else:
                for i, count in enumerate(possiblePredictions):
                    if count == maxCount:
                        move = i
                        break                
                confidenceInSequenceFound = 1.0

            confidenceInSequence = (i + 1) / len(turnsToCheck)
            confidence = (confidenceInSequence * 0.75) + (confidenceInSequenceFound * 0.25)
                                
            if bestConfidence < confidence:
                if Debug:
                    print ("Sequence to look for:          ", seq)
                    print ("Position of latest found seq:  ", history.rfind(seq, 0, currentTurn - 1))

                if Debug and bestConfidence != -1:
                    print ("confidence changed from %.2f to %.2f" % (bestConfidence, confidence))
                    
                bestConfidence = confidence 
                bestMove = move              
                
            return move, confidence         # uncomment this to check all the turns

    if Debug and bestConfidence >= 0:
        print ("Current history:               ", history)
        print ("Enemy move predicted:          ", bestMove)
        print ("Confidence:                    ", bestConfidence)
        input()
            
    return bestMove, bestConfidence
        
    return 1, 0
    return rps.biased_roshambo (1/3.0, 1/3.0), 0
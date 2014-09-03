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
    
    for i, turn in enumerate(turnsToCheck):
        if turn > currentTurn:
            continue
            
        seq = history[-turn:]
        found = history.rfind(seq, 0, currentTurn - 1)
                
        if found != -1:
            end = found + len(seq)
            move = history[end:end + 1]
            move = int(move)
            confidence = 1 - (i / len(turnsToCheck))
            if Debug:
                print ("Sequence to look for:   ", seq)
                print ("Position of found seq:  ", found)
                print ("Location of end of seq: ", end)
                print ("Current history:        ", history)
                print ("Enemy move predicted:   ", move)
                print ("Confidence:             ", confidence)
                input()
                
            
            return move, confidence       
        
    return 1, 0
    return rps.biased_roshambo (1/3.0, 1/3.0), 0
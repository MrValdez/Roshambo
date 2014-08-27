import rps

enemyHistory = ""
    
def play(a):
    currentTurn = rps.getTurn()
    
    if currentTurn == 0:
        return 1, 0
        
    myMoveLastTurn = rps.myHistory(currentTurn)
    enemyMoveLastTurn = rps.enemyHistory(currentTurn)

    global enemyHistory
    enemyHistory += str(enemyMoveLastTurn)
    history = enemyHistory
    
    turnsToCheck = [1, 2, 3, 4, 5, 10, 15, 20, 25, 50]
    for turn in reversed(turnsToCheck):
        if turn > currentTurn:
            continue
            
        seq = history[-turn:]
        found = history.rfind(seq, 0, currentTurn - 1)
                
        if found != -1:
            start = found+len(seq)
            move = history[start:start + 1]
            move = int(move)
            #print ("seq", seq)
            #print ("found", found)
            #print ("start", start)
            #print ("hisrory", history)
            #print ("move: ", move)
            #input()
            confidence = 1
            return move, confidence
        
        
    move = (rps.enemyHistory(currentTurn) + 1) % 3
    confidence = 1
    return move, confidence
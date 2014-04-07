import rps
def yomi():
    turn = rps.myHistory(0)
    
    #print("Current Turn: ", turn)
    #print("My history: ", rps.myHistory(turn))
    #print("Enemy history: ", rps.enemyHistory(turn))
    #input()
    return (rps.enemyHistory(turn) + 1) % 3
    
def isVerbose():
    """If 1 is returned, print the result of each trial."""
    #return 1
    return 0
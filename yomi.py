import BeatFrequentPick

def yomi(targetTurn):
    #return BeatFrequentPick.move(targetTurn)
    return 0

def SkeletonAI():
    """ This is the most basic AI that shows the functions used """
    currentTurn = rps.myHistory(0)
    
    if currentTurn:
        myMoveLastTurn = rps.myHistory(currentTurn - 1)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn - 1)
    
    return (rps.enemyHistory(currentTurn) + 1) % 3
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    return False
import BeatFrequentPick

def yomi(targetTurn):
    return BeatFrequentPick.move(targetTurn)

def SkeletonAI():
    currentTurn = rps.myHistory(0)
    myMoveLastTurn = rps.myHistory(turn)
    enemyMoveLastTurn = rps.enemyHistory(turn)
    
    #input()
    return (rps.enemyHistory(turn) + 1) % 3
    
def isVerbose():
    """If True is returned, print the result of each trial."""
    return False
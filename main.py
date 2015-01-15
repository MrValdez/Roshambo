import yomi


def play(a):
    decision = yomi.play(a)

    return decision
    
def isVerbose():
    return yomi.Debug
    
def shutdown():
    yomi.shutdown()
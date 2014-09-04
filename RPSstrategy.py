import rps

class RPSstrategy:
    def __init__(self):
        self.reset()
        
    def reset(self):
        pass
    
    def update(self):
        pass
    
    def play(self):
        ownPlay = rps.random() % 3
        playConfidence = 0
        return ownPlay, playConfidence

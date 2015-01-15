import random
random.seed(0)

import yomi

import configparser
class cDNA:
    path_input  = "results/input/"
    path_output = "results/output/"
    
    def __init__(self):
        #self.load("JustRock.txt")
        self.load("base.txt")
        
    def load(self, filename):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(cDNA.path_input + filename)         
        
        def cleanup(text):
            text = text.split("#")[0]
            text = text.strip()
            return text
        
        self.strategies             = [cleanup(spam) for spam in config["strategies"]]
        self.strategy_ranking       = [cleanup(spam) for spam in config["strategy ranking"]][0]
        self.predictors             = [cleanup(spam) for spam in config["predictors"]]
        self.predictor_ranking      = [cleanup(spam) for spam in config["predictor ranking"]][0]
        self.yomi_preferences       = [float(cleanup(spam)) for spam in config["yomi preferences"].values()]
        self.yomi_score_preferences = [float(cleanup(spam)) for spam in config["yomi-score preferences"].values()]
        
        
dna = cDNA()

def play(a):
    decision = yomi.play(dna)

    return decision
    
def isVerbose():
    return yomi.Debug
    
def shutdown():
    yomi.shutdown()
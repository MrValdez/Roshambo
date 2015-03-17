import rps
import random
random.seed(0)

import yomi

import configparser
class cDNA:   
    def __init__(self, filename):
        if filename == -1: 
            self.strategies             = []
            self.strategy_ranking       = []
            self.predictors             = []
            self.predictor_ranking      = []
            self.yomi_preferences       = [0] * 3 * 3
            self.yomi_score_preferences = [0] * 3
        
            filename = "results/input/base.txt"
            self.load(filename)
        else:
            self.load(filename)
        
    def load(self, filename):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(filename)         
        
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
        
        # check if we should use Mersenne or the gcc rng
        if "rng" in config["info"] and \
            cleanup(config["info"]["rng"]).lower() == "gcc":
            rps.randomMersenne(False)
        else:
            rps.randomMersenne(True)
        
dna = None

def play(filename):
    global dna
    if dna == None:
        dna = cDNA(filename)
    decision = yomi.play(dna)

    return decision
    
def isVerbose():
    return yomi.Debug
    
def shutdown():
    yomi.shutdown()
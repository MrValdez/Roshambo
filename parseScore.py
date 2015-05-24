import click

import sys
import os

pathbase = "./results/output/"             # Note: this string should end with "/"
pathbase = "./DNAVillage/output_0/"             # Note: this string should end with "/"

def FindScore(bot, showresults):
    """Get the best and worst score of a bot against Yomi AI"""
    fileList = sorted(os.listdir(pathbase))
    fileList.reverse()      # for SeqPred

    bestScore = [0, -10000, ""] # "targetTurn", "score", "line"
    worstScore = [0, 10000, ""]
    
    gamesWon = 0
    gamesTied = 0
    gamesLost = 0
    
    for filename in fileList:
        if filename[-4:] != ".txt":
            if showresults:
                print("%s is not txt file" % (filename))
            continue
        
        variable = filename.split(".")[0]
            
        with open(pathbase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()
            found = text.upper().find(bot.upper())
            if found == -1:
                print ("Warning: %s not found in %s" % (bot, filename))
                continue
            line = text[text.rfind("\n", 0, found):text.find("\n", found)].strip()
            if showresults:
                print ("%s:\n %s" % (variable, line))
            
            scoreText = line[line.find("Match:") + len("Match:"):]
            score = scoreText[0:scoreText.find("(")].strip()
            score = int(score)
            
            if score > bestScore[1]:
                bestScore[0] = filename
                bestScore[1] = score
                bestScore[2] = line
            if score < worstScore[1]:
                worstScore[0] = filename
                worstScore[1] = score
                worstScore[2] = line
                
            if score > 50: gamesWon += 1
            elif score < -50: gamesLost += 1
            else: gamesTied += 1
        
    AInamesPos = bestScore[2].find("Match:")
    if bestScore[2][:AInamesPos] != worstScore[2][:AInamesPos]:
        return False, None, None, None, None, None
    else:
        return True, bestScore, worstScore, gamesWon, gamesLost, gamesTied
        
def DisplayScore(bestScore, worstScore, gamesWon, gamesLost, gamesTied):
    print ("")
    print ("Best Score : %s  Variant: %s\n %s" % (bestScore[1], bestScore[0], bestScore[2]))
    print ("")
    print ("Worst Score: %s  Variant: %s\n %s" % (worstScore[1], worstScore[0], worstScore[2]))    
    print ("")
    print ("Variants won: %i. Variants Lost: %i. Variants tied: %i" % (gamesWon, gamesLost, gamesTied))

def DisplayLatex(bot, bestScore, worstScore):
    print ("%s & WS = %s & %s & WS = %s & %s \\\\ \\hline" % 
            (bot, bestScore[0].count(",") + 1, bestScore[1], worstScore[0].count(",") + 1, worstScore[1]))
            # MBFP: (bot, int(bestScore[0]), bestScore[1], int(worstScore[0]), worstScore[1]))

@click.command()
@click.option("--bot", default=None, help="Name of bot to parse")
@click.option("--showresults", default=False, help="A value of True means the points gained from all variants are shown")
@click.option("--showlatex", default=False, help="A value of True means that the code for a latex table is outputted instead.")
def main(bot, showresults = False, showlatex = False):

    if bot == None:
        bots = """Good Ole Rock
R-P-S 20-20-60
Rotate R-P-S
Beat The Last Move
Always Switchin
Beat Frequent Pick
* Pi
* Switch A Lot
* Flat
* Anti-Flat
* Foxtrot
* De Bruijn
* Text
* Anti-rotn
* Copy-drift
* Add-react
* Add-drift
Iocaine Powder
Phasenbott
MegaHAL
RussRocker4
Biopic
Simple Modeller
Simple Predictor
Robertot
Boom
Shofar
ACT-R Lag2
Majikthise
Vroomfondel
Granite
Marble
ZQ Bot
Sweet Rocky
Piedra
Mixed Strategy
Multi-strategy
Inocencio
Peterbot
Bugbrain
Knucklehead""".split("\n")
    else:
        bots = [bot]
        
    for currentBot in bots:
        if showlatex == False and showresults == False: 
            print ("Searching for %s" % currentBot)

        success, bestScore, worstScore, gamesWon, gamesLost, gamesTied = FindScore (currentBot, showresults)
        if success:
            if showlatex:
                DisplayLatex(currentBot, bestScore, worstScore)
            else:
                DisplayScore(bestScore, worstScore, gamesWon, gamesLost, gamesTied)
        else:
            print ("\n************ Warning: Best score AI does not match worst score AI. Use a longer search string")

if __name__ == "__main__":
    main()
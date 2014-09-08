import sys
import os

pathbase = "./results/"             # Note: this string should end with "/"

def FindScore(bot, showAllResults):
    """Get the best and worst score of a bot against Yomi AI"""
    fileList = sorted(os.listdir(pathbase))
    bestScore = [0, -1000, ""] # "targetTurn", "score", "line"
    worstScore = [0, 1000, ""]
    
    gamesWon = 0
    gamesTied = 0
    gamesLost = 0
    
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename[-8:-4]
            
        with open(pathbase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()
            found = text.upper().find(bot.upper())
            if found == -1:
                print ("Warning: %s not found in %s" % (bot, filename))
                continue
            line = text[text.rfind("\n", 0, found):text.find("\n", found)].strip()
            if showAllResults:
                print ("%s: %s" % (variable, line))
            
            scoreText = line[line.find("Match:") + len("Match:"):]
            score = scoreText[0:scoreText.find("(")].strip()
            score = int(score)
            
            if score > bestScore[1]:
                bestScore[0] = variable
                bestScore[1] = score
                bestScore[2] = line
            if score < worstScore[1]:
                worstScore[0] = variable
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
    print ("Best Score : %s  targetRank: %s\n %s" % (bestScore[1], bestScore[0], bestScore[2]))
    print ("")
    print ("Worst Score: %s  targetRank: %s\n %s" % (worstScore[1], worstScore[0], worstScore[2]))    
    print ("")
    print ("Variants won: %i. Variants Lost: %i. Variants tied: %i" % (gamesWon, gamesLost, gamesTied))

def DisplayLatex(bot, bestScore, worstScore):
    print ("%s & MBFP\\textsubscript{%s} & %s & MBFP\\textsubscript{%s} & %s \\\\ \\hline" % 
            (bot, int(bestScore[0]), bestScore[1], int(worstScore[0]), worstScore[1]))

bot = None
showAllResults = False
showLatex = False

if len(sys.argv) >= 2: bot = None if sys.argv[1].isdigit() and (int(sys.argv[1]) == 0) else sys.argv[1]         # painful
if len(sys.argv) >= 3: showAllResults = True if int(sys.argv[2]) > 0 else False
if len(sys.argv) >= 4: showLatex = True if int(sys.argv[3]) > 0 else False

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
    if showLatex == False and showAllResults == False: 
        print ("Searching for %s" % currentBot)

    success, bestScore, worstScore, gamesWon, gamesLost, gamesTied = FindScore (currentBot, showAllResults)
    if success:
        if showLatex:
            DisplayLatex(currentBot, bestScore, worstScore)
        else:
            DisplayScore(bestScore, worstScore, gamesWon, gamesLost, gamesTied)
    else:
        print ("\n************ Warning: Best score AI does not match worst score AI. Use a longer search string")
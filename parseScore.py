import sys
import os

pathbase = "./results/"

def FindScore(bot, showAllResults):
    """Get the best and worst score of a bot against Yomi AI"""
    print ("Searching for %s" % bot)
    fileList = sorted(os.listdir(pathbase))
    bestScore = [0, 0, ""] # "targetTurn", "score", "line"
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
        
    print ("")
    print ("Best Score : %s  targetRank: %s\n %s" % (bestScore[1], bestScore[0], bestScore[2]))
    print ("")
    print ("Worst Score: %s  targetRank: %s\n %s" % (worstScore[1], worstScore[0], worstScore[2]))    
    print ("")
    print ("Variants won: %i. Variants Lost: %i. Variants tied: %i" % (gamesWon, gamesLost, gamesTied))

bot = "Iocaine"
bot = "Rock"
bot = "20-60"
bot = "Inocencio"
showAllResults = False

if len(sys.argv) >= 2: bot = sys.argv[1]
if len(sys.argv) >= 3: showAllResults = True if int(sys.argv[2]) > 0 else False

"""
usage:
python parseScore.py [bot partial name (case sensitive)] [show results? (value of 1 for true)]

example usage:
python parseScore.py Iocaine
python parseScore.py 20-60 1
"""

FindScore (bot, showAllResults)
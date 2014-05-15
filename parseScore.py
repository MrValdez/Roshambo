import os

filebase = "./results/results_from_py/"

def FindScore(bot, showAllResults = False):
    """Get the best and worst score of a bot against Yomi AI"""
    fileList = sorted(os.listdir(filebase))
    bestScore = [0, 0, ""] # "targetTurn", "score", "line"
    worstScore = [0, 1000, ""]
    
    gamesWon = 0
    gamesTied = 0
    gamesLost = 0
    
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename[-8:-4]
            
        with open(filebase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()
            found = text.find(bot)
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
    print ("Games won: %i Games Lost: %i Games tied: %i" % (gamesWon, gamesTied, gamesLost))

#FindScore("Iocaine")
FindScore("Rock")
#FindScore("20-60", True)
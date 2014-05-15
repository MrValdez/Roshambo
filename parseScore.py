import os

filebase = "./results/results_from_py/"

def FindScore(bot):
    """Get the best and worst score of a bot against Yomi AI"""
    fileList = sorted(os.listdir(filebase))
    bestScore = [0, 0, ""] # "targetTurn", "score", "line"
    worstScore = [0, 1000, ""]
    
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
        
    print ("Best Score : %s  targetRank: %s\n %s" % (bestScore[1], bestScore[0], bestScore[2]))
    print ("")
    print ("Worst Score: %s  targetRank: %s\n %s" % (worstScore[1], worstScore[0], worstScore[2]))

FindScore("Iocaine Powder")
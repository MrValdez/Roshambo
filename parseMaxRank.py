import sys
import os

pathbase = "./results/"             # Note: this string should end with "/"

def FindRank():
    """Get the highest and lowest rank of a bot against Yomi AI"""
    fileList = sorted(os.listdir(pathbase))

    # filename, Tournament score, Match score
    scores = [[file, 0, 0] for file in fileList]

    for i, filename in enumerate(fileList):
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename.split(".")[0]
        variable = variable[8:]
            
        with open(pathbase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()
            
            # Tournament score
            start = text.find("Tournament results:")
            entry = text.find("Yomi AI", start)
            score = text[entry - 3:entry]
            score = int(score)            
            
            scores[i][1] = score
            
            # Match score
            start = text.find("Match results:")
            entry = text.find("Yomi AI", start)
            score = text[entry - 3:entry]
            score = int(score)            
            
            scores[i][2] = score

    return scores

sortByTournament = True
rankings = FindRank()

if sortByTournament:
    rankings.sort(key=lambda i:i[1])
else:
    rankings.sort(key=lambda i:i[2])

print ("Tournament  Match                   Variant")
print (" Results   Results  ")
for rank in rankings:
    name = rank[0]
    name = name[8:-4]
    print("   %s %s %s" % (str(rank[1]).ljust(9), str(rank[2]).ljust(5), name))

import os
import subprocess
#import charts

pathbase = "./results/"             # Note: this string should end with "/"

MatchPts = 100
TournamentPts = 100
argv = [2]

def main():
    global argv
    PlayTournament(2, priorityMatch = True)
#    #PlayTournament(10, priorityTournament = True)
    CreateCSV()
#    charts.startPlotting()


def PlayTournament(size, priorityMatch = False, priorityTournament = False):
    global argv
    nextSeqSize = max(argv)
    while size > 0:
        size -= 1
        nextSeqSize += 1
        argv.append(nextSeqSize)
        filename = pathbase + "results %s.txt" % (str(argv))
        print ("\nRunning %s..." % (filename), end='')
        
        argument = ",".join([str(s) for s in argv])
        output = subprocess.check_output(["full.exe", argument], universal_newlines = True)
        with open(filename, "w") as f:
            stdout = str(output)
            f.write(stdout)
        
        header = "Match results"
        resultMatch = int(GetRank(output, header))
        header = "Tournament results"
        resultTournament = int(GetRank(output, header))

        global MatchPts
        global TournamentPts    
        if priorityMatch:
            if resultMatch < MatchPts:
                MatchPts = resultMatch
            else:
                argv.remove(nextSeqSize)

        if priorityTournament:
            if resultMatch < TournamentPts:
                TournamentPts = resultMatch
            else:
                argv.remove(nextSeqSize)
     
def GetRank(text, header):
    """
    Get the rank under header.
    Possible Headers:  Tournament results, Match results
    """
    headerStart = text.find(header)
    found = text.find("Yomi AI", headerStart)
    if found == -1:
        raise exception("MAJOR PARSING ERROR. Yomi AI text not found.")
        
    end = text.find("Yomi AI", found)
    start = end - 4
    rank = str(text[start:end].strip())
    
    return rank

def CreateCSV(outputFilename = "results"):
    """Create CSV by looking at the rank of the Yomi AI"""
    csv = ["", ""]
    fileList = sorted(os.listdir(pathbase))
    best = [[0, 100], [0, 100]] #variable, rank
    
    prettyWidth = 18
    print("\n\n%s  RANK   VARIABLE" % ("HEADER".ljust(prettyWidth)))
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        start = filename.find("[")
        end = filename.find("]")
        variable = filename[start:end + 1]
            
        with open(pathbase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()

            header = "Match results"
            rank = GetRank(text, header)
            print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))            
            csv[0] += "%s,%s\n" % (variable, rank)
            if int(rank) < best[0][1]:
                best[0][0] = variable
                best[0][1] = int(rank)
            
            header = "Tournament results"
            rank = GetRank(text, header)
            print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))
            csv[1] += "%s,%s\n" % (variable, rank)
            if int(rank) < best[1][1]:
                best[1][0] = variable
                best[1][1] = int(rank)    

    print ("\n")
    print ("Best Match Result      is variant %s with rank of %i" % (best[0][0], best[0][1]))
    print ("Best Tournament Result is variant %s with rank of %i" % (best[1][0], best[1][1]))
    
    file = "%s_%s.csv" % (outputFilename, "match")
    with open(file, "w") as f:
        f.write(csv[0])
    
    file = "%s_%s.csv" % (outputFilename, "tournament")
    with open(file, "w") as f:
        f.write(csv[1])
      
if __name__ == "__main__":
    main()
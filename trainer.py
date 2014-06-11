import os
import subprocess
import charts

pathbase = "./results/"             # Note: this string should end with "/"

def main():
    PlayTournament(1000)
    CreateCSV()
    charts.startPlotting()

def PlayTournament(size):
    for argv in range(1, size + 1):
        filename = pathbase + "results %s.txt" % (str(argv).zfill(4))
        print ("Running %s..." % (filename), end='')
        
        output = subprocess.check_output(["go.exe", str(argv)], universal_newlines = True)
        with open(filename, "w") as f:
            stdout = str(output)
            f.write(stdout)
        
        print("done")

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
    print("%s  VARIABLE    RANK" % ("HEADER".ljust(prettyWidth)))
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename[-8:-4]
            
        with open(pathbase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()

            header = "Match results"
            rank = GetRank(text, header)
            print ("%s]  %s        %s" % (header.ljust(prettyWidth), variable, rank))            
            csv[0] += "%s,%s\n" % (variable, rank)
            if int(rank) < best[0][1]:
                best[0][0] = variable
                best[0][1] = int(rank)
            
            header = "Tournament results"
            rank = GetRank(text, header)
            print ("%s]  %s        %s" % (header.ljust(prettyWidth), variable, rank))
            csv[1] += "%s,%s\n" % (variable, rank)
            if int(rank) < best[1][1]:
                best[1][0] = variable
                best[1][1] = int(rank)    

    print ("\nBest Match Result      is variant %s with rank of %i" % (best[0][0], best[0][1]))
    print ("\nBest Tournament Result is variant %s with rank of %i" % (best[1][0], best[1][1]))
    
    file = "%s_%s.csv" % (outputFilename, "match")
    with open(file, "w") as f:
        f.write(csv[0])
    
    file = "%s_%s.csv" % (outputFilename, "tournament")
    with open(file, "w") as f:
        f.write(csv[1])
      
if __name__ == "__main__":
    main()
import os
import subprocess

filebase = "./results/results_from_py"

def main():
    PlayTournament(1000)
    CreateCSV()

def PlayTournament(size):
    for argv in range(1, size + 1):
        filename = filebase + "results %s.txt" % (str(argv).zfill(4))
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
    fileList = sorted(os.listdir(filebase))
    
    prettyWidth = 18
    print("%s  VARIABLE    RANK" % ("HEADER".ljust(prettyWidth)))
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename[-8:-4]
            
        with open(filebase + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()

            header = "Match results"
            rank = GetRank(text, header)
            print ("%s]  %s        %s" % (header.ljust(prettyWidth), variable, rank))            
            csv[0] += "%s,%s\n" % (variable, rank)
            
            header = "Tournament results"
            rank = GetRank(text, header)
            print ("%s]  %s        %s" % (header.ljust(prettyWidth), variable, rank))
            csv[1] += "%s,%s\n" % (variable, rank)
        

    file = "%s_%s.csv" % (outputFilename, "match")
    with open(file, "w") as f:
        f.write(csv[0])
    
    file = "%s_%s.csv" % (outputFilename, "tournament")
    with open(file, "w") as f:
        f.write(csv[1])
      
if __name__ == "__main__":
    main()
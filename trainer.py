import os
import subprocess

filebase = "./results/"

def main():
    PlayTournament(1000)
    CreateCSV("results3.csv")

def PlayTournament(size):
    for argv in range(size):
        filename = filebase + "results %s.txt" % (str(argv).zfill(4))
        print ("Running %s..." % (filename), end='')
        
        output = subprocess.check_output(["go.exe", str(argv)], universal_newlines = True)
      
        with open(filename, "w") as f:
            stdout = str(output)
            f.write(stdout)
        
        print("done")

def CreateCSV(outputFilename = "results.csv"):
    """Create CSV by looking at the rank of the Yomi AI"""
    csv = ""
    ranks = []
    fileList = sorted(os.listdir(filebase))
    
    print("VARIABLE    RANK")
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
        
        variable = filename[-8:-4]]
    
        with open(filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()
            found = text.rfind("Yomi AI")
            if found == -1:
                print("MAJOR PARSING ERROR")
                break
                
            start = text.rfind("\n", 0, found - 4)
            end = text.find("Yomi AI", found)
            
            rank = str(text[start:end].strip())
            ranks.append(rank)
            
            print (" %s        %s" % (variable, rank))            
            csv += "%s,%s\n" % (variable, rank)

    with open(outputFilename, "w") as f:
        f.write(csv)
        
main()
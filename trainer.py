import random
random.seed(0)

import os
import subprocess
import charts

import configparser

Debug = True
Debug = False

MatchPts = 100
TournamentPts = 100

def main(path_input, path_output):
    files = os.listdir(path_input)
    completed = os.listdir(path_output)
    
    basepath, DNA_Name, _ = path_input.split("/")
    
    print ("")
    for file in files:
        Validate(path_input, file)
    
    with open(basepath + "/" + DNA_Name + ".txt", "w") as f:        
        for i, file in enumerate(files):
            print ("%i/%i: %s " % (i + 1, len(files), file), end='')
            if file == "mutating": continue     # skip evolve's mutating mark
            
            if file in completed:
                print ("[skipping] ", end='')
            else:
                PlayTournament(path_input, path_output, file)    
                print ("[done] ", end='')

            resultMatch, resultTournament = ReadRank(path_output + file)
            rank = "(Rank: %i. %i)" % (resultMatch, resultTournament)
            print(rank)
            
            f.write("%s %s\n" % (rank, file))
            
    print ("")

    csv, bestMatchResult, bestTournamentResult, AIList = GetHighestRank(path_output)

#    CreateCSV(path_output, path_output + "data.txt")
#    charts.startPlotting()

def Validate(path_input, filename):
    filename = path_input + filename
    
    if Debug: print ("Validating %s" % (filename))
    
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(filename)
    
    def cleanup(text):
        text = text.split("#")[0]
        text = text.strip()
        return text

    try:
        #[cleanup(spam) for spam in config["info"]]
        [cleanup(spam) for spam in config["strategies"]]
        [cleanup(spam) for spam in config["strategy ranking"]][0]
        [cleanup(spam) for spam in config["predictors"]]
        [cleanup(spam) for spam in config["predictor ranking"]][0]
        [float(cleanup(spam)) for spam in config["yomi preferences"].values()]
        [float(cleanup(spam)) for spam in config["yomi-score preferences"].values()]
    except KeyError as e:
        print("Error in", filename)
        raise e

def PlayTournament(path_input, path_output, filename):
    input_filename = path_input + filename
    output_filename = path_output + filename

    if filename in os.listdir(path_output): #check if file already exists
        if Debug: print (output_filename + " already exists")
        return
    
#    output = subprocess.call(["full.exe", input_filename], shell = True)
    output = subprocess.check_output(["full.exe", input_filename], universal_newlines = True)
#    output = subprocess.check_output(["iocaine.exe", input_filename], universal_newlines = True)
    with open(output_filename, "w") as f:
        stdout = str(output)
        f.write(stdout)

def ReadRank(results_filename):
    with open(results_filename, "r")  as f:
        output = f.read()
        
    header = "Match results"
    resultMatch = int(GetRank(output, header))
    header = "Tournament results"
    resultTournament = int(GetRank(output, header))
    
    return (resultMatch, resultTournament)
        
def GetRank(text, header):
    """
    Get the rank under header.
    Possible Headers:  Tournament results, Match results
    """
    headerStart = text.find(header)
    found = text.find("Yomi AI", headerStart)
    if found == -1:
        raise Exception("MAJOR PARSING ERROR. Yomi AI text not found.")
        
    end = text.find("Yomi AI", found)
    start = end - 4
    rank = str(text[start:end].strip())
    
    return rank

def GetHighestRank(path_output):
    """
    Get the highest possible rank from output directory.
    Returns csv of all files, best Match Result, and best Tournament Result 
    """
    
    csv = ["", ""]
    fileList = sorted(os.listdir(path_output))
    best = [[0, 100], [0, 100, 0]] #variable, rank
    AIList = []
    
    prettyWidth = 18
    #if Debug: print("\n\n%s  RANK   VARIABLE" % ("HEADER".ljust(prettyWidth)))
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("skipping %s" % (filename))
            continue
                
        start = filename.find("[")
        end = filename.find("]")
        variable = filename[start:end + 1]
            
        with open(path_output + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()

            matchRank = GetRank(text, "Match results")
            #if Debug: print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))            
            
            variable = variable[-3:].replace("]","").replace("[","").strip()
            csv[0] += "%s,%s\n" % (variable, matchRank)
            if int(matchRank) < best[0][1]:
                best[0][0] = filename
                best[0][1] = int(matchRank)
            
            tournamentRank = GetRank(text, "Tournament results")
            #if Debug: print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))
            
            variable = variable[-3:].replace("]","").replace("[","").strip()
            csv[1] += "%s,%s\n" % (variable, tournamentRank)

            
            if int(tournamentRank) < best[1][1]:
                best[1][0] = filename
                best[1][1] = int(tournamentRank)    

                tournamentResultStr = """ Tournament results:
    Player Name          total 
  1 Yomi AI"""
                found = text.find(tournamentResultStr)
                tournamentPoints = text[found + len(tournamentResultStr):text.find("\n", found + len(tournamentResultStr))]
                tournamentPoints = tournamentPoints.strip()

                best[1][2] = int(tournamentPoints)

            AIList.append((filename, (int(matchRank), int(tournamentRank))))
            
    AIList.sort(key = lambda a:(a[1][0], a[1][1]))

    print ("\n")

    print ("Best Match Result")
    for AI in AIList:
        if AI[1][0] != best[0][1]:  break
        
        print(" Rank %i.%i [%s]" % (AI[1][0], AI[1][1], AI[0]))

    print ("Best Tournament Result [%s] with rank of %i (%i)" % (best[1][0], best[1][1], best[1][2]))
    
    return csv, best[0], best[1], AIList

def CreateCSV(path_output, output_filename = None):
    """Create CSV from GetHighestRank"""
    csv, bestMatchResult, bestTournamentResult, AIList = GetHighestRank(path_output)
    
    if outputFilename != None:
        file = "%s_%s.csv" % (outputFilename, "match")
        with open(file, "w") as f:
            f.write(csv[0])
        
        file = "%s_%s.csv" % (outputFilename, "tournament")
        with open(file, "w") as f:
            f.write(csv[1])
  
if __name__ == "__main__":
    main(path_input = "results/input/", path_output = "results/output/")
    #main(path_input = "DNAVillage/input_1/", path_output = "DNAVillage/output_1/")
   
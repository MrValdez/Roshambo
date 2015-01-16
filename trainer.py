import os
import subprocess
import charts

import configparser

path_input  = "results/input/"
path_output = "results/output/"

files = ["base.txt"]
files = ["JustRandom.txt"]
files = os.listdir(path_input)

MatchPts = 100
TournamentPts = 100

def main():
    for file in files:
        Validate(file)

    print ("")
    
    for file in files:
        PlayTournament(file)
        
    print ("")
    
    for file in files:
        CreateLatex(file)

#    CreateCSV(path_output + "data.txt")
#    charts.startPlotting()

def Validate(filename):
    filename = path_input + filename
    
    print ("Validating %s" % (filename))
    
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(filename)
    
    def cleanup(text):
        text = text.split("#")[0]
        text = text.strip()
        return text

    [cleanup(spam) for spam in config["strategies"]]
    [cleanup(spam) for spam in config["strategy ranking"]][0]
    [cleanup(spam) for spam in config["predictors"]]
    [cleanup(spam) for spam in config["predictor ranking"]][0]
    [float(cleanup(spam)) for spam in config["yomi preferences"].values()]
    [float(cleanup(spam)) for spam in config["yomi-score preferences"].values()]

def PlayTournament(filename):
    input_filename = path_input + filename
    output_filename = path_output + filename

    if filename in os.listdir(path_output): #check if file already exists
        print (output_filename + " already exists")
        return

    print ("Running %s..." % (filename), end='')
        
    output = subprocess.check_output(["full.exe", input_filename], universal_newlines = True)
    with open(output_filename, "w") as f:
        stdout = str(output)
        f.write(stdout)
        print (" done")
        
    header = "Match results"
    resultMatch = int(GetRank(output, header))
    header = "Tournament results"
    resultTournament = int(GetRank(output, header))
        
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

def CreateCSV(output_filename = None):
    """Create CSV by looking at the rank of the Yomi AI"""
    csv = ["", ""]
    fileList = sorted(os.listdir(path_output))
    best = [[0, 100], [0, 100]] #variable, rank
    
    prettyWidth = 18
    print("\n\n%s  RANK   VARIABLE" % ("HEADER".ljust(prettyWidth)))
    for filename in fileList:
        if filename[-4:] != ".txt":
            print("%s is not txt file" % (filename))
                
        start = filename.find("[")
        end = filename.find("]")
        variable = filename[start:end + 1]
            
        with open(path_output + filename) as f:
            # find the rank of the Yomi AI            
            text = f.read()

            header = "Match results"
            rank = GetRank(text, header)
            print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))            
            #csv[0] += "%s,%s\n" % (variable, rank)
            
            variable = variable[-3:].replace("]","").replace("[","").strip()
            csv[0] += "%s,%s\n" % (variable, rank)
            if int(rank) < best[0][1]:
                best[0][0] = variable
                best[0][1] = int(rank)
            
            header = "Tournament results"
            rank = GetRank(text, header)
            print ("%s]  %s     %s" % (header.ljust(prettyWidth), rank.rjust(2), variable))
            #csv[1] += "%s,%s\n" % (variable, rank)
            
            variable = variable[-3:].replace("]","").replace("[","").strip()
            csv[1] += "%s,%s\n" % (variable, rank)

            if int(rank) < best[1][1]:
                best[1][0] = variable
                best[1][1] = int(rank)    

    print ("\n")
    print ("Best Match Result      is variant [%s] with rank of %i" % (best[0][0], best[0][1]))
    print ("Best Tournament Result is variant [%s] with rank of %i" % (best[1][0], best[1][1]))

    if outputFilename != None:
        file = "%s_%s.csv" % (outputFilename, "match")
        with open(file, "w") as f:
            f.write(csv[0])
        
        file = "%s_%s.csv" % (outputFilename, "tournament")
        with open(file, "w") as f:
            f.write(csv[1])

def CreateLatex(filename):      
    print ("Building latex for %s." % (filename))

    title = filename.split(".")[0]
    text = r"""The full results are found at Table \ref{table:%s_results}.
    
\begin{table*}
    \caption{%s results}
    \label{table:%s_results}
    \centering
    \begin{tabular}{|l|c|c|c|c|}
        \hline
        \textbf{Vs bot} & \textbf{Total score} & \textbf{Wins} & \textbf{Losts} & \textbf{Ties} \\ \hline
""" % (title, title, title)

    with open(path_output + filename) as f:
        f.readline()
        f.readline()
        
        while True:
            line = f.readline()
            splitPos = line.find("vs")
            
            if splitPos == -1:
                break
            
            line = line[splitPos + 2:]
            bot, score = line.split("Match:")
            bot = bot.strip(" * ")
            bot = bot.strip()
            score = score.strip()
            
            total, score = score.split("(")
            wins, score  = score.split("+")
            losts, score = score.split("-")
            ties, score = score.split("=")
            
            total = total.strip()
            wins  = wins.strip()
            losts = losts.strip()
            ties  = ties.strip()
            
            text += "%s & %s & %s & %s & %s \\\\ \\hline \n" % (bot, total, wins, losts, ties)

        text = text.strip() + """
        \end{tabular}
    \end{table*}"""

        line = None
        while True:
            line = f.readline()
            if line.find("Yomi AI") >= 0:
                break
        TournamentRank, score = line.split("Yomi AI")
        TournamentRankPoints = score.strip().split(" ")[0]
        
        line = None
        while True:
            line = f.readline()
            if line.find("Yomi AI") >= 0:
                break
        MatchRank, score = line.split("Yomi AI")
        score = score.split(" ")
        score = [spam for spam in score if spam != ""]
        MatchRankTotals, MatchRankWins, MatchRankLosts, MatchRankDraws = score[0:4]
        
#        text += "\n\nTournament Rank: %s (%s)\nMatch Rank: %s (%s) (%s+ %s- %s=)" % \
#                (TournamentRank.strip(), TournamentRankPoints, 
#                 MatchRank.strip(), MatchRankTotals, MatchRankWins, MatchRankLosts, MatchRankDraws)

        text += "\n\n"
        text += "The Match rank is %s with a total points of %s (%s win, %s losts and %s ties). " % (MatchRank.strip(), MatchRankTotals, MatchRankWins, MatchRankLosts, MatchRankDraws)
        text += "The Tournament rank is %s with %s points." % (TournamentRank.strip(), TournamentRankPoints)

    file = path_output + title + ".tex"
    with open(file, "w") as f:
        f.write(text)

  
if __name__ == "__main__":
    main()
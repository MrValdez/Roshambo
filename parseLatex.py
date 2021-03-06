import os
import configparser

def CreateLatex(path_input, path_output, filename):      
    print ("Building latex for %s." % (filename))

    title = filename.split(".")[0]
    text = r"""The full results are found in Table \ref{table:%s_results} with the winning matches highlighted. A summary can be found at Table \ref{table:ranking_summary}.""" % (title)
    
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(path_input + filename)
    description = config["info"]["name"].strip("\"")
    
    table = r"""
\begin{table}
    \caption{Results of %s against the different bots}
    \label{table:%s_results}
    \centering
    \begin{tabular}{|l|c|c|c|c|}
        \hline
        \textbf{Bot} & \textbf{Total} & \textbf{Wins} & \textbf{Losses} & \textbf{Ties} \\ \hline
""" % (description, title)

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
            
            highlight = ""
            if int(total) >= 50:
                highlight = r"\rowcolor{HighlightRowColor} "
            table += "%s%s & %s & %s & %s & %s \\\\ \\hline \n" % (highlight, bot, total, wins, losts, ties)
        table = table.strip() + """
        \end{tabular}
    \end{table}"""

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

        text += " The Match rank is %s with a total score of %s points (%s win, %s losses, and %s ties). " % (MatchRank.strip(), MatchRankTotals, MatchRankWins, MatchRankLosts, MatchRankDraws)
        text += "The Tournament rank is %s with %s points." % (TournamentRank.strip(), TournamentRankPoints)
        text = text + "\n\n" + table

    file = path_output + title + ".tex"
    with open(file, "w") as f:
        f.write(text)

def ParseLatex(path_input, path_output):
    files = os.listdir(path_output)

    for file in files:
        CreateLatex(path_input, path_output, file)
        
if __name__ == "__main__":
    ParseLatex(path_input = "results/input/", path_output = "results/output/")
    #ParseLatex(path_input = "DNAVillage/input_0/", path_output = "DNAVillage/output_0/")
    #ParseLatex(path_input = "DNAVillage/input_190/", path_output = "DNAVillage/output_190/")
    #ParseLatex(path_input = "DNAVillage_Best_result/input/", path_output = "DNAVillage_Best_result/output/")
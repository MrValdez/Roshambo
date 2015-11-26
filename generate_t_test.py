'''
This script will generate a csv of the match and tournament results with or without Yomi, for different individual predictors.
    1. Generate the configuration for all individual predictors with and without Yomi (todo)
    2. Run the trainer for all the configurations (todo)
    3. Gather the data from the results
    4. From the csv, generate the latex table (todo)
'''
import os
import csv
import numpy as np

from collections import OrderedDict
from scipy.stats import ttest_ind, ttest_rel

def gather_data(path):
    match_title = "Yomi AI is match ranked"
    tournament_title = "Yomi is tournament ranked"
    completed = os.listdir(path)

    results = OrderedDict()

    for file in completed:
        # we are only interested in lower bound
        if file.find("UB") >= 0:
            continue
    
        match_rank = -1
        tournament_rank = -1
        
        with open(path + file) as f:
            file_data = f.read()
        
        for title in (match_title, tournament_title):
            start = file_data.find(title)
            end = file_data.find("\n", start)
            found = file_data[start + len(title):end]
            found = found.strip()

            if title == match_title:
                match_rank = int(found)
            elif title == tournament_title:
                tournament_rank = int(found)
            else:
                raise

#        print ("{}\n Match: {}\n Tournament {}".format(file, match_rank, tournament_rank))
        title = file
        title = title.replace(".txt", "").strip()
        title = title.replace(" LB", "").strip()

        if "Yomi" not in file:
            key_match = "match"
            key_tournament = "tournament"
        else:
            title = title.replace("Yomi", "").strip()
            key_match = "yomi_match"
            key_tournament = "yomi_tournament"
        
        if title not in results:
            results[title] = {}
            
        results[title][key_match] = match_rank
        results[title][key_tournament] = tournament_rank

    results_list = []
    difference = 0
    for title, row in results.items():
        try:
            s = "{}, {}, {}, {}".format(title, row['match'], row['tournament'], row['yomi_match'], row['yomi_tournament'])
            results_list.append(s)
            
            difference += row['yomi_match'] - row['match']
        except KeyError:
            print("incomplete results not found with " + title)
            print("only found the following:")
            for key, value in row.items():
                print(" {}: {}".format(key, value))
            del results[title]
    result_str = "\n".join(results_list)
    
    #print(result_str)
    print("Match rank difference between yomi and without yomi: %i" % (difference))
    print("Average match rank difference: %f" % (difference / len(results_list)))

    return results
 
def printData(results):
    #final_output = "Test, Match, Tournament, Yomi Match, Yomi Tournament\n"
    #print (final_output)
        
    # show the inputs
    print("{}| No yomi | Yomi".format(" ".ljust(10)))
    print("--------------------------")
    for key, data in results.items():
        title = key
        no_yomi, yomi = str(data['match']), str(data['yomi_match'])
        print("{}| {} | {}".format(title.ljust(10),
                                   no_yomi.rjust(7),
                                   yomi.rjust(2)))
    

def createLatex(results):
    description = "t-tests data"
    title = "t_test_data"
    table = r"""
\begin{table}
\centering
\resizebox{.80\width}{!}{\begin{minipage}[t]{\textwidth}
    \caption{%s results}
    \label{table:%s}
    \centering
    \begin{tabular}{|l|c|c|}
        \hline
        \textbf{Predictor used} & {\specialcell[b]{\textbf{Match results}\\\textbf{without Yomi}}} & {\specialcell[b]{\textbf{Match results}\\\textbf{with Yomi}}} \\ \hline
""" % (description, title)
    
    for key, data in results.items():
        title = key.split()
        if title[0][:3] == "HSP":  title[0] = title[0][:3] + r" (WS=" + title[0][3:] + ")"
        if title[0][:4] == "MBFP": title[0] = title[0][:4] + r"\textsubscript{" + title[0][4:] + "}"
        title = title[0] + r"\\" + " ".join(title[1:])
                
        no_yomi, yomi = data['match'], data['yomi_match']
 
        #table += "%s & %s & %s \\\\ \\hline \n" % (title, no_yomi, yomi)
        table += "\specialcell[x]{%s} & %s & %s \\\\ \\hline \n" % (title, no_yomi, yomi)

    table = table.strip() + """
    \end{tabular}
\end{minipage} }
\end{table}"""

    file = "t_test.tex"
    with open(file, "w") as f:
        f.write(table)
    print("\nT-test table saved to " + file)

def t_tests(results):
    no_yomi_results = [d['match'] for d in results.values()]
    yomi_results = [d['yomi_match'] for d in results.values()]

    print("")
    print("Mean for no yomi group: ", np.mean(no_yomi_results))
    print("Mean for yomi group: ", np.mean(yomi_results))

    print("")
    print("t-test for two independent samples: ")
    t, prob = ttest_ind(no_yomi_results, yomi_results, equal_var=False)
    print(" t-statistic:        {}\n two-tailed p-value: {}".format(t, prob))
    
    print("")
    
    print("t-test on two related samples: ")
    t, prob = ttest_rel(no_yomi_results, yomi_results)
    print(" t-statistic:        {}\n two-tailed p-value: {}".format(t, prob))

                     
# from openoffice calc:
# average: -1.6451612903
# one-paired: 4.35681893802403E-006
# two-paired: 8.71363787604805E-006

def main(path_input = 't_test_data/input/', path_output = 't_test_data/output/'):
    data = gather_data(path_output)
    printData(data)
    t_tests(data)
    createLatex(data)

if __name__ == "__main__":
    main()
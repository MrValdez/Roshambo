'''
This script will generate a csv of the match and tournament results with or without Yomi, for different individual predictors.
    1. Generate the configuration for all individual predictors with and without Yomi
    2. Run the trainer for all the configurations
    3. Generate the csv based on the results
    4. From the csv, generate the latex table (todo)    
'''
import os

from collections import OrderedDict
from scipy.stats import ttest_ind, ttest_rel

def generate_csv(path):
    match_title = "Yomi AI is match ranked"
    tournament_title = "Yomi is tournament ranked"
    completed = os.listdir(path)

    results = OrderedDict()

    for file in completed:
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
        title = file.replace(".txt", "").strip()

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

    #final_output = "Test, Match, Tournament, Yomi Match, Yomi Tournament\n"
    #print (final_output)
        
    # show the inputs
    #print(result_str)
    print("{}| No yomi | Yomi".format(" ".ljust(10)))
    print("--------------------------")
    for key, data in results.items():
        no_yomi, yomi = str(data['match']), str(data['yomi_match'])
        title = key
        print("{}| {} | {}".format(title.ljust(10),
                                   no_yomi.rjust(7),
                                   yomi.rjust(2)))

    no_yomi_results = [d['match'] for d in results.values()]
    yomi_results = [d['yomi_match'] for d in results.values()]
    
    print("Match rank difference between yomi and without yomi: %i" % (difference))
    print("Average match rank difference: %f" % (difference / len(results_list)))

    print("")
    print("t-test for two independent samples: ")
    t, prob = ttest_ind(no_yomi_results, yomi_results, equal_var=False)
    print(" t-statistic:        {}\n two-tailed p-value: {}".format(t, prob))
    
    print("")
    
    print("t-test on two related samples: ")
    t, prob = ttest_rel(no_yomi_results, yomi_results)
    print(" t-statistic:        {}\n two-tailed p-value: {}".format(t, prob))
                     
# from openoffice calc:
# one-paired: 4.35681893802403E-006
# average: -1.6451612903
# two-paired: 8.71363787604805E-006

def main(path_input = 't_test_data/input/', path_output = 't_test_data/output/'):
    csv = generate_csv(path_output)


if __name__ == "__main__":
    main()
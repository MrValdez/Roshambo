'''
This script will generate a csv of the match and tournament results with or without Yomi, for different individual predictors.
    1. Generate the configuration for all individual predictors with and without Yomi (todo)
    2. Run the trainer for all the configurations (todo)
    3. Generate the csv based on the results (todo)
    4. From the csv, generate the latex table (todo)    
'''
import os

from collections import OrderedDict

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

        print ("{}\n Match: {}\n Tournament {}".format(file, match_rank, tournament_rank))
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
    for title, row in results.items():
        try:
            s = "{}, {}, {}, {}".format(title, row['match'], row['tournament'], row['yomi_match'], row['yomi_tournament'])
            results_list.append(s)
        except KeyError:
            print("results not found with " + title)
    results = "\n".join(results_list)

    final_output = "Test, Match, Tournament, Yomi Match, Yomi Tournament\n"
    print (final_output)
    print(results)

def main(path_input = 't_test_data/input/', path_output = 't_test_data/output/'):
    csv = generate_csv(path_output)


if __name__ == "__main__":
    main()
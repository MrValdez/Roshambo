#define rock      0
#define paper     1
#define scissors  2

extern int *my_history;
extern int *opp_history;

/*

Training Program

A training program creates a list of all possible moves that can be performed. The program then creates scenarios and assigns which moves can be used. The assigned moves are then sorted from optimal to the least effective by the scenario analysis program.

Scenario Analysis Program

The Scenario Aanalysis program will rank each move of its effectiveness, given a particular scneario. Given an infinite set of possible moves, only a small set should be used 
    

*/

int yomi()
{
    my_history[0];                  // number of games
    my_history[my_history[0]];     // my previous move

    opp_history[0];                  // opponent's number of games
    opp_history[opp_history[0]];    // opponent's previous move

    int move = random() % 3;

    return(move);
}

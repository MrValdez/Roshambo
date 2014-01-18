// RoShamBo Tournament Test Suite structures

#define rock      0
#define paper     1
#define scissors  2

extern int my_history[];
extern int opp_history[];

#define null            0
#define maxYomiLayer    3

/////////////////////////////

/*

Training Program

A training program creates a list of all possible moves that can be performed. The program then creates scenarios and assigns which moves can be used. The assigned moves are then sorted from optimal to the least effective by the scenario analysis program.

Scenario Analysis Program

The Scenario Aanalysis program will rank each move of its effectiveness, given a particular scneario. Given an infinite set of possible moves, only a small set should be used 
    

*/

// In theory, changing just the personality should change the behavior of the AI
typedef struct sPersonality
{
    // See onrespect section
    int initialRespectOnOpponent;     
    int initialDisrespectOnOpponent;
    float respectModifier;
    float disrespectModifier;
    int respectTreshold;
} sPersonality;

typedef struct situation
{
    int chosenMove;         // the move to play in the given situation
    
    int situationSize;          // holds how large the situation array is
    int situation[1000];       // a struct to determine the situation. game dependent
    
    int successRate;        // Can go up or down if the AI wins or lose a turn, respectively. Default: 0
    int successRateAsCounter;  // refers to how likely this will be used as a counter move (higher yomi layer)
    
    #define UNINITIALIZED_VALUE -1000
    int enemyRespect;       // See onrespect section
    
    int counterSize;
    struct situation** counter;
} situation;

typedef struct database
{
    int size;
    situation** situations;
} database;

//global variables. because c
database* YomiDatabase;
sPersonality* personality;

database* createDatabase();
sPersonality* developPersonality();
database* trainingProgram(database* db);
database* analysisProgram(database* db);
void debugShow(database* db);
situation* selectSituation(database* db, int currentTurn);

// Initiailize the yomi AI
void initYomi()
{
    database* db = createDatabase();
    personality = developPersonality();
    //debugShow(db);

    db = trainingProgram(db);
    db = analysisProgram(db);
    
    YomiDatabase = db;
}

// Add counter to current situation's list of counters
void addCounter(situation* currentSituation, situation* foundCounter)
{
    currentSituation->counter = (situation**) realloc (currentSituation->counter, sizeof(situation*) * (currentSituation->counterSize + 1));
    currentSituation->counter[currentSituation->counterSize] = foundCounter;
    currentSituation->counterSize++;
}

// Given a situation, find the appropriate counter in the database
// and add it to its list of possible counters
// Question: If a counter can't be found, what should the AI do?
void findCounter(database* db, situation* currentSituation)
{    
    situation* iterSituation;
    int i;

    // Check the entire database
    for (i = 0; i < db->size; i++)
    {
        situation* foundCounter = null;
        
        iterSituation = db->situations[i];
        if (iterSituation == currentSituation)
            // Don't check a situation against itself.
            continue;
            
        // Look for a counter and temporary assign the
        // move+situation to foundCounter
        switch (currentSituation->chosenMove)
        {
            case rock:      
                if (iterSituation->chosenMove == paper)
                    foundCounter = iterSituation;
                break;
            case paper:      
                if (iterSituation->chosenMove == scissors)
                    foundCounter = iterSituation;
                break;
            case scissors:      
                if (iterSituation->chosenMove == rock)
                    foundCounter = iterSituation;
                break;
        }
        
        // Add the counter to the pool
        if (foundCounter != null)
        {
/*            printf("counter found for %i: %i\n", 
                    currentSituation->chosenMove,
                    foundCounter->chosenMove);
*/
            addCounter(currentSituation, foundCounter);
        }
    }
}

// Create a blank situation to be filled up
situation *createSituation(database* db)
{
    situation* newSituation;
    newSituation = (situation*) malloc(sizeof(situation));
    newSituation->situationSize = 0;
    //newSituation->situation[0] = "";
    //strcpy(newSituation->situation, "RPS");

    newSituation->successRate = 0;
    newSituation->successRateAsCounter = 0;
    newSituation->enemyRespect = UNINITIALIZED_VALUE;

    newSituation->counterSize = 0;
    newSituation->counter = (situation**) malloc (sizeof(situation*));

    db->situations = (situation**) realloc (db->situations, sizeof(situation*) * (db->size + 1));
    db->situations[db->size] = newSituation;
    db->size = db->size + 1;
    
    return newSituation;
}

database* createDatabase()
{
    // Parse all possible moves in a neutral sitatuion (game specific)
    database* db = (database*) malloc(sizeof(database));
    db->situations = (situation**) malloc(sizeof(situation*));
    db->size = 0;
    
    return db;
}

sPersonality* developPersonality()
{
    sPersonality *Personality = (sPersonality*) malloc(sizeof(sPersonality));

    // Dummy data
    Personality->initialRespectOnOpponent = 100;
    Personality->initialDisrespectOnOpponent = 30;
    Personality->respectModifier = 30;
    Personality->disrespectModifier = 10;
    Personality->respectTreshold = 70;

    return Personality;
}

void debugSituation(situation* currentLayer, int layerNumber)
{    
    if (currentLayer == null || layerNumber > maxYomiLayer)
        return;

    int j;
    for (j = 0; j < layerNumber; j++)
        printf(" ");
        
    switch(currentLayer->chosenMove)
    {
        case rock: printf("rock");
                    break;
        case paper: printf("paper");
                    break;
        case scissors: printf("scissors");
                    break;
    }
    
    printf("\n");

    int k;
    for (k = 0; k < currentLayer->counterSize; k++)
    {
        debugSituation(currentLayer->counter[k], layerNumber + 1);
    }
}

void debugShow(database* db)
{
    int i, j, k, layerNumber;
    for (i = 0; i < db->size; i++)
    {
        situation* currentSituation = db->situations[i];
        debugSituation(currentSituation, 0);
        printf("\n");
    }

    printf("**** End of debug print ****\nPress any key to continue...");
    getch();
    exit(1);
}

// Game dependent
struct database* trainingProgram(struct database* db)
{
    situation* newSituation;
    
    // neutral game
    newSituation = createSituation(db);
    newSituation->chosenMove = rock;

    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
     
    newSituation = createSituation(db);
    newSituation->chosenMove = scissors;

    // counter situations
    newSituation = createSituation(db);
    newSituation->chosenMove = rock;
    newSituation->situation[0] = scissors;
    newSituation->situationSize++;

    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
    newSituation->situation[0] = rock;
    newSituation->situationSize++;
     
    newSituation = createSituation(db);
    newSituation->chosenMove = scissors;
    newSituation->situation[0] = paper;
    newSituation->situationSize++;
    
    int i;
    for (i = 0; i < db->size; i++)
    {
        situation* currentSituation = db->situations[i];
        findCounter(db, currentSituation);
    }
    
    return db;
}

struct database* analysisProgram(struct database* db)
{
    return db;
}

typedef int bool;
const int True = 1;
const int False = 0;

void evaluateTurn(database* db, int currentTurn, int playerMove, int oppMove)
{
    //Check if we are victorious on turn.
    //Ties are not considered as a victory.
    // If we won, 
    //  increase successRate
    //  If successRate is not 100, 
    //   decrease enemyRespect by Personality.disrespectModifier
    // If we lost,
    //  decrease successRate
    //  increase RespectModifier by Personality.respectModifier
    //  check if situation evaluated has an entry with the opponent's counter
    //   if it doesn't exist, add the new situation (flag for saving into database)
    //   update successRateForCounter.
    
    //todo: the successrate should be averaged, not added or multiplied
    
    bool victory = 
        (playerMove == rock && oppMove == scissors) ||
        (playerMove == paper && oppMove == rock) ||
        (playerMove == scissors && oppMove == paper);
        
    situation *currentSituation = selectSituation(db, currentTurn);   // a optimization is to store the last situation in memory instead of recomputing it.
    if (currentSituation == null)
    {
        //Something is wrong.
        printf ("fatal error: selectSituation is not deterministic");
        return;
    }
   
    if (victory)
    {
        currentSituation->successRate += (int) (currentSituation->successRate * 0.5f);
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialDisrespectOnOpponent;
        else
            currentSituation->enemyRespect -= personality->disrespectModifier;
    }
    else
    {
        currentSituation->successRate -= (int) (currentSituation->successRate * 0.25f);
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialRespectOnOpponent;
        else
            currentSituation->enemyRespect += personality->respectModifier;

        //printf("Lost at turn %i\n", currentTurn);
        //printf("respect value:%i\n", currentSituation->enemyRespect);
//    getch();
    }

    // limit from -100 to +100
    currentSituation->successRate = currentSituation->successRate > 100 ? 100 : currentSituation->successRate;
    currentSituation->successRate = currentSituation->successRate < -100 ? -100 : currentSituation->successRate;
    currentSituation->enemyRespect = currentSituation->enemyRespect > 100 ? 100 : currentSituation->enemyRespect;
    currentSituation->enemyRespect = currentSituation->enemyRespect < -100 ? -100 : currentSituation->enemyRespect;

    
    // find the counter that the opponent used
    // todo: we could have multiple situations where the move is used. gather all of them and predict which
    int i;
    for (i = 0; i < currentSituation->counterSize; i++)
    {
        situation *counter = currentSituation->counter[i];
        counter->successRateAsCounter += 1;
    } 
}


int yomi()
{
    int currentTurn = my_history[0]; // number of games
    my_history[my_history[0]];       // my previous move

    opp_history[0];                  // opponent's number of games
    opp_history[opp_history[0]];     // opponent's previous move
    
    /*
    // 1. Evaluate current situation.
            Situations can exist multiple times but with different moves. 
    // 2. Find current situation in database.
    // 3. Rank situations.
    // 4. Choose move based on situation and opponent variables (likelihood of countering, etc).
    // 5. Update situation chosen by outcome of turn.
            Flag this as new for farther training
    */

    database* db = YomiDatabase;        // Get the global database

    // 5. (Because of how the test suite works, 5 is run first to check the previous turn
    if (currentTurn > 0)
    {
        int lastTurn = currentTurn;
        int lastPlayerMove = my_history[lastTurn];
        int lastOppMove = opp_history[lastTurn];
        evaluateTurn(db, lastTurn, lastPlayerMove, lastOppMove);
    }
    
    int move = selectSituation(db, currentTurn)->chosenMove;

    //todo: free(situation);
    return move;    
}

situation* selectSituation(database* db, int currentTurn)
{
    // 1.
    char* currentSituation = null;
    int currentSituationSize = currentTurn;
    
    if (currentTurn == 0)
    {
        // Game is starting. Use a favored move.
        currentSituation = null;
        currentSituationSize = 0;
    }
    else
    {
        // Situations for Roshambo is alternation of enemy and player moves
        currentSituation = (char*) malloc (sizeof(char*) * (currentTurn * 2));
        currentSituationSize = currentTurn;
        int i, j;
        
        j = 0;
        for (i = currentSituationSize; i > 0; i--)
        {
            currentSituation[j+0] = opp_history[i];
            currentSituation[j+1] = my_history[i];
            j+=2;
        }
    }

    // 2.
    int responsesCount = 0;
    situation** responses = (situation**) malloc (sizeof(situation**));
    
    int i;
    situation* possibleResponse;
    bool considerResponse;

    if (currentSituation == null)
    {
        // first move.
        for (i = 0; i < db->size; i++)
        {
            possibleResponse = db->situations[i];
            
            if (possibleResponse->situationSize == 0)
            {            
                responses = (situation**) realloc (responses, sizeof(situation*) * (responsesCount + 1));
                responses[responsesCount] = possibleResponse;
                responsesCount++;
            }
        }
    }
    else
    {
        for (i = 0; i < db->size; i++)
        {
            possibleResponse = db->situations[i];
            
            // Roshambo specific scenario check
            considerResponse = True;
            int j, k;
            for (k = 0, j = 0; k < possibleResponse->situationSize && j < currentSituationSize; k++, j++)
            {
                if (possibleResponse->situation[j] != currentSituation[k])
                {
                    considerResponse = False;
                    break;
                }
            }
            
            if (considerResponse == True)            
            { 
                responses = (situation**) realloc (responses, sizeof(situation*) * (responsesCount + 1));
                responses[responsesCount] = possibleResponse;
                responsesCount++;
            }
        }
    }
    
    // if no response was found, then we need to record the new situation
    if (responsesCount == 0)
    {
//        printf("no responses found.");getch();
        //todo:
        responses[0] = db->situations[0];
    }
   
    //3.
    {
        situation** tempResponses = responses;
        situation** sortedResponses = (situation**) malloc (sizeof(situation**) * responsesCount);
        situation* current = null;
        
        /////////////////////
        // Sort by more defined situations
        
        // find max
        int i, j = 0;
        int max = 0;
        for (i = 0; i < responsesCount; i++)
        {
            current = tempResponses[i];

            if (current->situationSize > max)
                max = current->situationSize;
        }

//        printf("\nMAX%i %i\n\n", max, responsesCount);
        for (; max >= 0; max--)
        {
            for (i = 0; i < responsesCount; i++)
            {
                current = tempResponses[i];
//                printf("%i == %i\n", current->situationSize, max);
                if (current->situationSize == max)
                {
//                    printf("added %i\n", j);
                    sortedResponses[j++] = current;
                }
            }
        }
        
        responses = sortedResponses;
    }

    //debug
    if (responsesCount > 1)
    {
//          printf ("%i responses found", responsesCount);getch();
    }
    /* debug
    printf("\nPossible responses found: %i\n", responsesCount);
    int j;
    for (i=0; i< responsesCount; i++)
    {
        printf("%io.%i\n", i, responses[i]->situationSize);
        for (j = 0; j < responses[i]->situationSize; j++)
        {
            printf("%i %i %i\n", i, j, responses[i]->situation[j]);
        }
    }
//    printf("Prediction: %i Chosen move: %i\n", responses[0]->situation[0]->chosenMove, responses[0]->chosenMove);
    getch();    //*/
    

    ////////////////////
    
    
    ////////////////////
    // Sort by etc
    ////////////////////
    
    
    //4.
    situation* chosenResponse = responses[0];
    
    // Check if the AI should respect the opponent
    if (chosenResponse->enemyRespect > personality->respectTreshold)
    {
//    printf("I have respect");getch();
        // We respect that our opponent will counter our move. So we select the counter to their counter
        if (chosenResponse->counterSize)
        {
            situation *enemyChoice;
            int currentSuccessRateAsCounter = -1000;
            int i;

            // Yomi Layer 1
            // in case of multiple counters, evaluate what are more likely to be chosen based on successRateAsCounter.
            // todo: make this into a list
            for (i = 0; i < chosenResponse->counterSize; i++)
            {
                if (chosenResponse->counter[i]->successRateAsCounter > currentSuccessRateAsCounter)
                {
                    enemyChoice = chosenResponse->counter[i];
                    currentSuccessRateAsCounter = enemyChoice->successRateAsCounter;
                }
            }

            // evaluate the likely responses and see if we need to go to the Yomi Layer 2.
            // todo: make this into a list
            situation *yomiLayer2 = enemyChoice->counter[0];
        
            chosenResponse = yomiLayer2;
        }
        else
        {
            // we don't know how to react. Normally, the trainer program will cover this, but in case something unexpected happens, we should have a neutral answer (or a safe answer?)
           // todo: implement above algo
           chosenResponse = db->situations[0];           
        }
    }
    

    return chosenResponse;
}

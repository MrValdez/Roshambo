// RoShamBo Tournament Test Suite structures

#define rock      0
#define paper     1
#define scissors  2

extern int *my_history;
extern int *opp_history;

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
struct personality
{
    // See onrespect section
    int initialRespectOnOpponent;     
    int initialDisrespectOnOpponent;
    float RespectModifier;
    float DisrespectModifier;
    int respectTreshold;
};

typedef struct situation
{
    int chosenMove;         // the move to play in the given situation
    int situation;          // a struct to determine the situation. game dependent
    int enemyRespect;       // See onrespect section
    
    int nextLayerSize;
    struct situation** nextLayer;
} situation;

typedef struct database
{
    int size;
    situation** situations;
} database;

database* createDatabase();
database* trainingProgram(database* db);
database* analysisProgram(database* db);
void debugShow(database* db);

// Initiailize the yomi AI
void initYomi()
{
    database* db = createDatabase();
    debugShow(db);

    db = trainingProgram(db);
    db = analysisProgram(db);
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
            currentSituation->nextLayer = (situation**) realloc (currentSituation->nextLayer, sizeof(situation*) * (currentSituation->nextLayerSize + 1));
            currentSituation->nextLayer[currentSituation->nextLayerSize] = foundCounter;
            currentSituation->nextLayerSize++;
        }
    }
}

database* createDatabase()
{
    // Parse all possible moves in a neutral sitatuion (game specific)
    database* db = (database*) malloc(sizeof(database));
    db->situations = (situation**) malloc(sizeof(situation*));
    db->size = 0;
    
    situation* newSituation;
    
    newSituation = (situation*) malloc(sizeof(situation));
    newSituation->chosenMove = rock;
    newSituation->situation = 0;
    newSituation->enemyRespect = 0;
    newSituation->nextLayerSize = 0;
    newSituation->nextLayer = (situation**) malloc (sizeof(situation*));
    db->situations = (situation**) realloc (db->situations, sizeof(situation*) * (db->size + 1));
    db->situations[db->size] = newSituation;
    db->size = db->size + 1;

    newSituation = (situation*) malloc(sizeof(situation));
    newSituation->chosenMove = paper;
    newSituation->situation = 0;
    newSituation->enemyRespect = 0;
    newSituation->nextLayerSize = 0;
    newSituation->nextLayer = (situation**) malloc (sizeof(situation*));
    db->situations = (situation**) realloc (db->situations, sizeof(situation*) * (db->size + 1));
    db->situations[db->size] = newSituation;
    db->size = db->size + 1;
 
    newSituation = (situation*) malloc(sizeof(situation));
    newSituation->chosenMove = scissors;
    newSituation->situation = 0;
    newSituation->enemyRespect = 0;
    newSituation->nextLayerSize = 0;
    newSituation->nextLayer = (situation**) malloc (sizeof(situation*));
    db->situations = (situation**) realloc (db->situations, sizeof(situation*) * (db->size + 1));
    db->situations[db->size] = newSituation;
    db->size = db->size + 1;

    int i;
    for (i = 0; i < db->size; i++)
    {
        situation* currentSituation = db->situations[i];
        findCounter(db, currentSituation);
    }
    
    return db;
}

void debugSituation(situation* currentLayer, int layerNumber)
{    
    if (currentLayer == null || layerNumber >= maxYomiLayer)
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
    for (k = 0; k < currentLayer->nextLayerSize; k++)
    {
        debugSituation(currentLayer->nextLayer[k], layerNumber + 1);
    }
}

void debugShow(database* db)
{
    int i, j, k, layerNumber;
    for (i = 0; i < db->size; i++)
    {
        situation* currentSituation = db->situations[i];
        debugSituation(currentSituation, 0);
    }

    printf("**** End of debug print ****\nPress any key to continue...");
    getch();
    exit(1);
}

struct database* trainingProgram(struct database* db)
{
}

struct database* analysisProgram(struct database* db)
{
}

int yomi()
{
    my_history[0];                  // number of games
    my_history[my_history[0]];     // my previous move

    opp_history[0];                  // opponent's number of games
    opp_history[opp_history[0]];    // opponent's previous move

    int move = random() % 3;

    return(move);
}

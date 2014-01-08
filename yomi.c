// RoShamBo Tournament Test Suite structures

#define rock      0
#define paper     1
#define scissors  2

extern int *my_history;
extern int *opp_history;

#define null      0

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

typedef struct layer
{
    int chosenMove;
    int situation;          // a struct to determine the situation. game dependent
    int enemyRespect;       // See onrespect section
    
    int layerNumber;           // Starts from 0 and ends with 4
    struct layer* nextLayer;     // nextLayer = null, if layerNumber = 0
} layer;

typedef struct database
{
    int size;
    layer** moves;
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

layer* findCounter(layer* currentLayer)
{
    layer* newLayer = (layer*) malloc(sizeof(layer));
    
    switch (currentLayer->chosenMove)
    {
        case rock:      newLayer->chosenMove = paper;
                        break;
        case paper:     newLayer->chosenMove = scissors;
                        break;
        case scissors:  newLayer->chosenMove = rock;
                        break;
    }
    
    newLayer->situation = 0;
    newLayer->enemyRespect = 0;
    newLayer->layerNumber = currentLayer->layerNumber + 1;
    
    if (newLayer->layerNumber < 4)
    {
        newLayer->nextLayer = findCounter(newLayer);
    }
    else
        newLayer->nextLayer = null;
    
    return newLayer;
}

database* createDatabase()
{
    // Parse all possible moves in a neutral sitatuion (game specific)
    database* db = (database*) malloc(sizeof(database));
    db->moves = (layer**) malloc(sizeof(layer*));
    db->size = 0;
    
    layer* newLayer;
    
    newLayer = (layer*) malloc(sizeof(layer));
    newLayer->chosenMove = rock;
    newLayer->situation = 0;
    newLayer->enemyRespect = 0;
    newLayer->layerNumber = 0;
    newLayer->nextLayer = findCounter(newLayer);
    db->moves = (layer**) realloc (db->moves, sizeof(layer*) * (db->size + 1));
    db->moves[db->size] = newLayer;
    db->size = db->size + 1;

    newLayer = (layer*) malloc(sizeof(layer));
    newLayer->chosenMove = paper;
    newLayer->situation = 0;
    newLayer->enemyRespect = 0;
    newLayer->layerNumber = 0;
    newLayer->nextLayer = findCounter(newLayer);
    db->moves = (layer**) realloc (db->moves, sizeof(layer*) * (db->size + 1));
    db->moves[db->size] = newLayer;
    db->size = db->size + 1;
 
    newLayer = (layer*) malloc(sizeof(layer));
    newLayer->chosenMove = scissors;
    newLayer->situation = 0;
    newLayer->enemyRespect = 0;
    newLayer->layerNumber = 0;
    newLayer->nextLayer = findCounter(newLayer);
    db->moves = (layer**) realloc (db->moves, sizeof(layer*) * (db->size + 1));
    db->moves[db->size] = newLayer;
    db->size = db->size + 1;
 
    return db;
}

void debugShow(database* db)
{
    int i, j;
    for (i = 0; i < db->size; i++)
    {
        layer* currentMove = db->moves[i];
        layer* currentLayer = currentMove;
        while (currentLayer != null)
        {
            printf("%i", currentLayer->layerNumber);
            for (j = 0; j < 4; j++)
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
            currentLayer = currentLayer->nextLayer;
        }
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

/*todo: remove duplicates when creating new situations
        make sure that our assumption for the offset for odd situations are correct
*/
// RoShamBo Tournament Test Suite structures

#define rock        0
#define paper       1
#define scissors    2
//wildcard is ? and is an unknown element or a prediction flag
#define wildcard    -1

extern int my_history[];
extern int opp_history[];

#define null            0
#define maxYomiLayer    4

#define DEBUG
#define DEBUG1
#define DEBUG2
//#define DEBUG2_VERBOSE
#define DEBUG3
#define DEBUG4
#define DEBUG5
///*/   

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
    int successRateTreshold; // the minimum amount of success rate we would consider

    // See onrespect section
    int initialRespectOnOpponent;     
    int initialDisrespectOnOpponent;
    float respectModifier;
    float disrespectModifier;
    int respectTreshold;
    
    int currentRespectOnEnemy;
    int respectOnEnemyTreshold;
    
} sPersonality;

typedef struct situation
{
    int chosenMove;         // the move to play in the given situation
    
    int situationSize;          // holds how large the situation array is
    int situation[1000];       // a struct to determine the situation. game dependent
    
    int successRate;        // Can go up or down if the AI wins or lose a turn, respectively. Default: 0
    int successRateAsCounter;  // refers to how likely this will be used as a counter move (higher yomi layer)

    int rankThisTurn; //goes up and down depending on score given by situation comparisions. reset every turn.
    
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
situation* lastSituationSelected;
int turnOfLastVictory = 0;

database* createDatabase();
sPersonality* developPersonality();
database* trainingProgram(database* db);
database* analysisProgram(database* db);
void debugShow(database* db);
situation* selectSituation(database* db, int currentTurn);
int* evaluateCurrentSituation(int currentTurn, int* currentSituationSize);

// Initiailize the yomi AI
void initYomi()
{
    database* db = createDatabase();
    personality = developPersonality();
    //debugShow(db);

    db = trainingProgram(db);
    db = analysisProgram(db);
    
    YomiDatabase = db;
    lastSituationSelected = null;
}

// Add counter to current situation's list of counters
void addCounter(situation* currentSituation, situation* foundCounter)
{
    //check first if counter is already in the situation's list
    int i;

#ifdef DEBUG1
/*
    printf("\n%i\n", currentSituation->counterSize);
    debugPrintSituation(foundCounter->situation, foundCounter->situationSize);
    printf("\n");
*/
#endif

    for (i = 0; i < currentSituation->counterSize; i++)
    {
#ifdef DEBUG1
/*
        debugPrintSituation(currentSituation->counter[i]->situation, currentSituation->counter[i]->situationSize);
        printf("\n");
        printf("move %i %i", currentSituation->chosenMove, foundCounter->chosenMove);
        printf("\n");
        printf("%i %i", currentSituation->counter[i], foundCounter);
        printf("\n");
*/
#endif
        if (currentSituation->counter[i] == foundCounter)
            return;
    }

    currentSituation->counter = (situation**) realloc (currentSituation->counter, sizeof(situation*) * (currentSituation->counterSize + 1));
    currentSituation->counter[currentSituation->counterSize] = foundCounter;
    currentSituation->counterSize++;
}

// Find a situation string in the database and return it.
// if move == wildcard, we don't check the move
// todo: its possible to have multiple situations found. return a list
situation* findSituation(database* db, int* Situation, int situationSize, int move)
{    
    situation* iterSituation;
    int i, j;    
    // Check the entire database
    for (i = 0; i < db->size; i++)
    {
        iterSituation = db->situations[i];
        
        if (iterSituation->situationSize != situationSize)
            continue;
        
        for (j = 0; j < iterSituation->situationSize; j++)
        {
            if (iterSituation->situation[j] != Situation[j])
            {
                iterSituation = null;
                break;
            }
        }
        
        if (iterSituation == null)
            continue;

        if (move != wildcard &&
            iterSituation->chosenMove != move)
            continue;
            
        return iterSituation;
    }
    
    return null;
}

// Create a blank situation to be filled up
situation *createSituation(database* db)
{
    situation* newSituation;
    newSituation = (situation*) malloc(sizeof(situation));
    newSituation->situationSize = 0;

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
    Personality->successRateTreshold = 0;
    
    Personality->initialRespectOnOpponent = 10;
    Personality->initialDisrespectOnOpponent = -10;
    Personality->respectModifier = 10;
    Personality->disrespectModifier = -5;
    Personality->respectTreshold = 20;

    Personality->currentRespectOnEnemy = 0;
    Personality->respectOnEnemyTreshold = 30;
    
    return Personality;
}

void debugSituation(situation* currentLayer, int layerNumber)
{    
    if (currentLayer == null || layerNumber > maxYomiLayer)
        return;

    int j;
    for (j = 0; j < layerNumber; j++)
        printf(" ");
        
    debugPrintSituation(currentLayer->situation, currentLayer->situationSize);
    printf(" (");
    
    switch(currentLayer->chosenMove)
    {
        case rock: printf("rock");
                    break;
        case paper: printf("paper");
                    break;
        case scissors: printf("scissors");
                    break;
    }
    
    printf(")");
    printf("\n");

    int k;
    for (k = 0; k < currentLayer->counterSize; k++)
    {
        debugSituation(currentLayer->counter[k], layerNumber + 1);
    }
}

void debugShow(database* db)
{
    printf("\n");
    int i, j, k, layerNumber;
    for (i = 0; i < db->size; i++)
    {
        situation* currentSituation = db->situations[i];
        debugSituation(currentSituation, 0);
        printf("\n");
    }

    printf("**** End of debug print ****\nPress any key to continue...");
    getch();
}

void debugPrintSituation(int* situation, int size)
{
#ifdef DEBUG
    int i;
    for (i = 0; i < size; i++)
    {
        if (situation[i] == wildcard)
            printf("_");
        else
        {
            printf("%i", situation[i]);
            /*switch(situation[i])
            {
                case rock:      printf("R"); break;
                case paper:     printf("P"); break;
                case scissors:  printf("S"); break;
            }*/
        }
    }
#endif
}

// Game dependent
struct database* trainingProgram(struct database* db)
{
    situation* newSituation;
    
    // neutral game
    situation* newSituation1 = createSituation(db);
    newSituation1->chosenMove = rock;

    situation* newSituation2 = createSituation(db);
    newSituation2->chosenMove = paper;
     
    situation* newSituation3 = createSituation(db);
    newSituation3->chosenMove = scissors;
    createYomiLayers(db, newSituation1, wildcard);
    createYomiLayers(db, newSituation2, wildcard);
    createYomiLayers(db, newSituation3, wildcard);
    
    return db;
}

situation* findCounter(database* db, situation *attackingSituation)
{
    int moveToCounterSituation = (attackingSituation->chosenMove + 1) % 3; //todo: roshambo specific.
    int i, j;

    for (i = 0; i < db->size; i++)
    {
        situation *currentSituation = db->situations[i];
        
/*      do we need this?  
        // we only check neutral moves
        if (currentSituation->situationSize > 2)
        {
#ifdef DEBUG
            printf("skipping move: %i\n", currentSituation->chosenMove);
#endif
            continue;
        } */
       if (currentSituation->situationSize > 0 &&
            currentSituation->situationSize == attackingSituation->situationSize)
        {        
            // in roshambo, we only need to account for the last move in the situation
            if (currentSituation->situation[currentSituation->situationSize - 1] == attackingSituation->situation[attackingSituation->situationSize - 1])
            {
                for (j = 0; j < currentSituation->counterSize; j++)
                {
                    //todo: what if we have multiple counters with the same response?
                    if (currentSituation->counter[j]->chosenMove == moveToCounterSituation)
                    {
                        return currentSituation->counter[j];
                    }
                }
            }
        }
        
        if (currentSituation->situationSize == 0 &&
            attackingSituation->situationSize == 0)
        {
            // check neutral moves
            for (j = 0; j < currentSituation->counterSize; j++)
            {
                //todo: what if we have multiple counters with the same response?
                if (currentSituation->counter[j]->chosenMove == moveToCounterSituation)
                {
                    return currentSituation->counter[j];
                }
            }
        }
    }

    return null;
}

struct database* analysisProgram(struct database* db)
{
    return db;
}

typedef int bool;
const int true = 1;
const int false = 0;

situation* createOneYomiLayer(database* db, int layerNumber, situation* previousYomiLayer, int oppMove)
{
    if (oppMove == wildcard && previousYomiLayer != null)
        oppMove = previousYomiLayer->chosenMove;
        
    int winningMove = (oppMove + 1) % 3;
    
    //todo: add wildcard prediction to findcounter
    //situation* newYomiLayer = findCounter(db, previousYomiLayer);
    //situation* newYomiLayer = findSituation(db, previousYomiLayer->situation, previousYomiLayer->situationSize, previousYomiLayer->chosenMove);
    
    situation* newYomiLayer = previousYomiLayer;

    if (newYomiLayer != null && newYomiLayer->counterSize)
        newYomiLayer = newYomiLayer->counter[0];
    else
        newYomiLayer = null;

    //situation* newYomiLayer = null;    
    
    if (newYomiLayer == null || newYomiLayer->chosenMove != winningMove)
    {
#ifdef DEBUG1
        printf("Creating new situation for yomi layer %i\n", layerNumber);
#endif

        //We did not find this counter situation in our database. Let's make one.
        //copy situation from previous yomi layer and put in this layer but add the prediction flag for player's choice
        newYomiLayer = createSituation(db);
        
        //choose a move that beats the previous layer.
        //todo: very roshambo specific.
        newYomiLayer->chosenMove = winningMove; 
        
        int i = 0;
        for (i = 0; i < previousYomiLayer->situationSize; i++)
        {
            newYomiLayer->situation[i] = previousYomiLayer->situation[i];
        }
        
        // add the prediction flag on the first yomi layer
/*        if (layerNumber == 1)
            newYomiLayer->situation[i++] = wildcard;
*/       
        newYomiLayer->situation[i++] = oppMove;     
        newYomiLayer->situationSize = i;
        
        // Layer 1 and 2 have a higher initial counter success rate than layer 3 and 4
        if (layerNumber <= 2)
        {
            newYomiLayer->successRateAsCounter += 50;    //todo: should be personality value
        }
        else
        {
            newYomiLayer->successRateAsCounter = 0;    //todo: should be personality value
        }
        
        // layer 1 is an enemy prediction
/*        if (layerNumber == 1)
        {
            newYomiLayer->enemyRespect = personality->initialRespectOnOpponent;   //todo: should be personality value
        }
        else*/
        {
            // other layers are basically new scenarios
            newYomiLayer->enemyRespect = UNINITIALIZED_VALUE;
        }
        
        addCounter(previousYomiLayer, newYomiLayer);
    }
    else
    {
#ifdef DEBUG1
        printf("Situation found in database: ");
#endif
    }
    
#ifdef DEBUG1
    printf("Yomi layer %i (", layerNumber);
    debugPrintSituation(newYomiLayer->situation, newYomiLayer->situationSize);
    printf(")\n Chosen move: %i.\n", newYomiLayer->chosenMove);
#endif
/*
    //check if yomiLayer1 has yomiLayer2 as its counter. If not, add it
    bool isInCounterList = false;
    int i;
    for (i = 0; i < previousYomiLayer->counterSize; i++)
    {
        if (previousYomiLayer->counter[i] == newYomiLayer)
        {
            isInCounterList = true;
            break;
        }
    }
    
    if (isInCounterList == false)
    {
#ifdef DEBUG1      
        printf("adding yomi layer %i as counter to yomi layer %i\n", layerNumber, layerNumber - 1);
#endif            
        addCounter(previousYomiLayer, newYomiLayer);
    }
 */   
    return newYomiLayer;
}

void createYomiLayers(database* db, situation* currentSituation, int oppMove)
{
    situation* yomiLayer0 = findSituation(db, currentSituation->situation, currentSituation->situationSize, currentSituation->chosenMove);

    if (yomiLayer0 == null)
    {
#ifdef DEBUG1
        printf("new situation found. creating situation for ");
        if (currentSituation != null)
            debugPrintSituation(currentSituation->situation, currentSituation->situationSize);
        printf("\n");
#endif

        yomiLayer0 = createSituation(db);
        int i;
        for (i = 0; i < currentSituation->situationSize; i++)
        {
            yomiLayer0->situation[i] = currentSituation->situation[i];
        }
        yomiLayer0->situationSize = currentSituation->situationSize;
        yomiLayer0->chosenMove = currentSituation->chosenMove;
    }
    
#ifdef DEBUG1
    printf("Yomi layer 0 (");
    debugPrintSituation(yomiLayer0->situation, yomiLayer0->situationSize);
    printf(")\n Chosen move: %i.\n", yomiLayer0->chosenMove);
#endif
    
    situation* yomiLayer1 = 
        createOneYomiLayer(db, 1, yomiLayer0, oppMove);
    situation* yomiLayer2 = 
        createOneYomiLayer(db, 2, yomiLayer1, wildcard);
    situation* yomiLayer3 = 
        createOneYomiLayer(db, 3, yomiLayer2, wildcard);
    situation* yomiLayer4 = 
        createOneYomiLayer(db, 4, yomiLayer3, wildcard);     
    
    //yomiLayer5 is the same as layer 2, so we loop this back.
    addCounter(yomiLayer4, yomiLayer2);

#ifdef DEBUG1
    printf("\n");
#endif

}

void evaluateTurn(database* db, int currentTurn, int playerMove, int oppMove)
{
    //Check if we are victorious on turn.
    //Ties are considered as a victory (todo: personality specific?).
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

    //tie check:
    //victory = victory || (playerMove == oppMove);
        
    situation *currentSituation = lastSituationSelected;
    if (currentSituation == null)
    {
        //Something is wrong.
#ifdef DEBUG
        printf ("fatal error: this is the first turn but we are already evaluating.");
#endif
        return;
    }
   
    if (victory)
    {
        currentSituation->successRate += 10;
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialDisrespectOnOpponent;
        else
            currentSituation->enemyRespect += personality->disrespectModifier;
    }
    else
    {
        // record the situation in the database where we received a lost.
        currentSituation->successRate -= 10;
        
        // increase our respect for the enemy
        personality->currentRespectOnEnemy += 10;
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialRespectOnOpponent;
        else
            currentSituation->enemyRespect += personality->respectModifier;

#ifdef DEBUG1
        printf("Lost. Updating situation ");
        debugPrintSituation(currentSituation->situation, currentSituation->situationSize);
        printf(":\n");
        printf(" Success rate:%i\n", currentSituation->successRate);
        printf(" Enemy respect value:%i\n", currentSituation->enemyRespect);
#endif

        //todo: this is the training program
        {
            int currentSituationSize = 0;
            int* currentSituation = evaluateCurrentSituation(currentTurn - 1, &currentSituationSize);
            
            situation* newSituation = findSituation(db, currentSituation, currentSituationSize, playerMove);
            
            if (newSituation == null)
            {
                newSituation = createSituation(db);
                int* currentSituation = evaluateCurrentSituation(currentTurn - 1, &currentSituationSize);
                int i;
                for (i = 0; i < currentSituationSize; i++)
                {
                    newSituation->situation[i] = currentSituation[i];
                }
                newSituation->situationSize = currentSituationSize;
                newSituation->chosenMove = playerMove;
            }
                        
            // create a new situation (if none exists) that is the counter to this turn's situation. 
            createYomiLayers(db, newSituation, oppMove);
        }
    }

    // limit from -100 to +100
    personality->currentRespectOnEnemy = personality->currentRespectOnEnemy > 100 ? 100 : personality->currentRespectOnEnemy;
    personality->currentRespectOnEnemy = personality->currentRespectOnEnemy < -100 ? -100 : personality->currentRespectOnEnemy;
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
    
#ifdef DEBUG1
    printf("======================\n\n");
#endif
}


int yomi()
{
    int currentTurn = my_history[0]; // number of games
    my_history[my_history[0]];       // my previous move

    opp_history[0];                  // opponent's number of games
    opp_history[opp_history[0]];     // opponent's previous move
    
    // Initialize database
    if (currentTurn == 0)
        initYomi();

    /*
    // 1. Evaluate current situation.
            Situations can exist multiple times but with different moves. 
    // 2. Find current situation in database. 
    //    Ignore situations with low success rate
    //    Use different checks to consider if situation is in play
    // 3. Rank situations.
    // 4. Apply yomi. Choose move based on situation and opponent variables (likelihood of countering, etc).
    // 5. Update situation chosen by outcome of turn.
            Flag this as new for farther training
    */

    database* db = YomiDatabase;        // Get the global database
    //debugShow(db);
    //reset the rankThisTurn for all situations to zero
    int i;
    for (i = 0; i < db->size; i++)
    {
        db->situations[i]->rankThisTurn = 0;
    }

#ifdef DEBUG
    if (currentTurn > 0)
    {
        getch();
        printf("\n=========BEGIN TURN #%i========\n", currentTurn);
    }
#endif

    // 5. (Because of how the test suite works, 5 is run first to check the previous turn
    if (currentTurn > 0)
    {
        int lastTurn = currentTurn;
        int lastPlayerMove = my_history[lastTurn];
        int lastOppMove = opp_history[lastTurn];
        evaluateTurn(db, lastTurn, lastPlayerMove, lastOppMove);
    }

    // 1 to 5
    lastSituationSelected = selectSituation(db, currentTurn);
    int move = lastSituationSelected->chosenMove;

#ifdef DEBUG
    printf("\nFinal Choice: %i", move);
    printf("\n=========END TURN #%i========\n", currentTurn);
#endif
    
    //todo: free(situation);
    return move;    
}

int* evaluateCurrentSituation(int currentTurn, int* currentSituationSize)
{
    int* currentSituation = null;

    if (currentTurn == 0)
    {
        // Game is starting. Use a favored move.
        currentSituation = null;
        *currentSituationSize = 0;
    }
    else
    {
        // Situations for Roshambo is alternation of player moves and enemy moves
        // Maximum situation size for Roshambo is 6 turns
        int i, j;
        int startTurn = currentTurn > 6 ? currentTurn - 6 : 0;
        int maxTurn = currentTurn;
        *currentSituationSize = (maxTurn - startTurn) * 2;
        currentSituation = (int*) malloc (sizeof(int*) * (*currentSituationSize));
                
        j = 0;
        for (i = startTurn; i < maxTurn; i++)
        {
            /* 
            roshambo specific: player history goes first, then opp history 
            todo: turn this into a struct
            */
        
            currentSituation[j+0] = my_history[i + 1];
            currentSituation[j+1] = opp_history[i + 1];
            j+=2;
        }
    }

#ifdef DEBUG
    printf("\nsituation for turn #%i is: ", currentTurn);
    debugPrintSituation(currentSituation, *currentSituationSize);
    printf("\n");
#endif
    
    return currentSituation;
}

bool compareSituation_Equal(situation* possibleResponse, int* currentSituation, int currentSituationSize)
{
    ////////////////////////////
    // If both situations are equal, it means this situation has already happened before
    ////////////////////////////

    if (possibleResponse->situationSize != currentSituationSize)
        return false;


    int i;
    bool isEqual = true;
    for (i = 0; i < currentSituationSize; i++)
    {
        if ((possibleResponse->situation[i] != currentSituation[i]) &&
            (possibleResponse->situation[i] != wildcard))
        {
            isEqual = false;
            break;
        }
    }

#ifdef DEBUG2_VERBOSE
    printf("Checking if both simulations are equal\n--=");
#endif
    
    if (isEqual)
    {
#ifdef DEBUG2_VERBOSE
        printf("  Both situations are equal\n");
#endif

        possibleResponse->rankThisTurn += 50;
    }
    else
    {
#ifdef DEBUG2_VERBOSE
        printf("  Both situations are not equal\n");
#endif
    }
    return isEqual;
}

//justCheckEnemyMoves: if true, we only check the enemy's moves and we ignore our own moves. This is here in case the enemy
//                     is not predicting our AI.
bool compareSituation_ToLastTurn_Check(situation* possibleResponse, int* currentSituation, int currentSituationSize, bool justCheckEnemyMoves, int offset, bool futureSituation)
{
    ////////////////////////////
    // Compare to last turn
    ////////////////////////////
    bool considerResponse = true;

    int j,k;

    considerResponse = true;
    for (j = 0, k = offset; j < possibleResponse->situationSize && k < currentSituationSize; j++, k++)
    {
        if (justCheckEnemyMoves && (j % 2 == 0))
        {
#ifdef DEBUG2_VERBOSE
            // Ignoring our previous move in case our enemy is doing a pattern and ignoring our own move
            printf ("Ignoring AI's previous move: %i\n", possibleResponse->situation[j]);
#endif
            continue;
        }
    
        if (possibleResponse->situation[j] != currentSituation[k] &&
            possibleResponse->situation[j] != wildcard)
        {
            considerResponse = false;
            break;
        }
    }

#ifdef DEBUG2
    if (considerResponse && offset)
    {
        printf("\nComparing the ff situations (offset: %i): \n", offset);
        for (j = 0; j < offset; j++)
            printf(" ");
        debugPrintSituation(possibleResponse->situation, possibleResponse->situationSize);
        printf("\n");
        debugPrintSituation(currentSituation, currentSituationSize);
        printf("\n");   
    } 
#endif
    
    return considerResponse;
}

bool compareSituation_ToLastTurn(situation* possibleResponse, int* currentSituation, int currentSituationSize)
{
#ifdef DEBUG2_VERBOSE
    printf("Checking Last Turn:\n--=\n");
#endif      

    int offset = 0;
    bool futureSituation;

    // we might get possible responses that are smaller than the current situation.
    // in this case, we have to compare the possible response to the end of the current situation.
    // by doing this, we can also consider situations that are small but don't have much history
    offset = currentSituationSize - possibleResponse->situationSize;
    
    // if the possible response has an odd length, we align accordingly
    futureSituation = possibleResponse->situationSize % 2 == 1;

    if (futureSituation)
        offset -= 1;
    if (offset < 0)
        offset = 0;

    bool CheckBothHistory = compareSituation_ToLastTurn_Check(possibleResponse, currentSituation, currentSituationSize, false, offset, futureSituation);
    bool justCheckEnemyMoves = compareSituation_ToLastTurn_Check(possibleResponse, currentSituation, currentSituationSize, true, offset, futureSituation);
    //justCheckEnemyMoves = false;
    
    bool considerResponse = CheckBothHistory || justCheckEnemyMoves;
    
    if (considerResponse == false)
    {
#ifdef DEBUG2_VERBOSE
        printf("Situation not the same\n");
#endif
    }
    else
    {
#ifdef DEBUG2_VERBOSE
        int j,k;
        
        for (j = 0, k = offset; j < possibleResponse->situationSize && k < currentSituationSize; j++, k++)
        {
            printf("%i == ", possibleResponse->situation[j]);
            printf("%i\n", currentSituation[k]);
        }
#endif
#ifdef DEBUG2
        printf("Situation similar to last turn");
        if (justCheckEnemyMoves ^ CheckBothHistory)
            printf(" (with only enemy moves are checked)");
        printf("\n");
#endif
        if (futureSituation == false)
        {
            possibleResponse->rankThisTurn += 30;
        }
        else
        {
            // if we offset, it means we are doing a prediction.
            // (uunahan na natin ang kalaban)
            // so we rank the next layer.

            int predictionModifier = 50;

            if (CheckBothHistory == false && justCheckEnemyMoves == true)
            {
                // we see a pattern with the enemy's movement (which we won't see if we don't look for patterns)
                // we don't give this a big rank for this because its possible that the pattern is a trap
                // todo: add a personality for likelihood of responding to possible baits.
                predictionModifier *= 0.5;
            }
            
            possibleResponse->counter[0]->rankThisTurn += predictionModifier;

#ifdef DEBUG2
            printf("--= Using a prediction. \nAdding rank to situation: ");
            debugPrintSituation(possibleResponse->counter[0]->situation, possibleResponse->counter[0]->situationSize);
            printf("\n");
#endif
            return false;
        }
        
    }
    
    return considerResponse;
}

situation* checkYomiLayer(database* db, situation* chosenResponse, int layerNumber)
{   
    // Check if the Yomi AI should respect the opponent on current situation
    int respectTresholdForLayer;
    int enemyRespect = chosenResponse->enemyRespect;
    
    if (layerNumber > 1) 
    {
        respectTresholdForLayer = personality->respectTreshold * (layerNumber - 1);        
//        enemyRespect = personality->currentRespectOnEnemy * 0.25 + enemyRespect * 0.75;  // Do we respect our enemy to apply yomi?
    }
    else
    {
        respectTresholdForLayer = personality->respectTreshold;
//        enemyRespect = personality->currentRespectOnEnemy * 0.30 + enemyRespect * 0.70;  // Do we respect our enemy to apply yomi?
    }
        
    if (enemyRespect >= respectTresholdForLayer
        //chosenResponse->successRate <= 0
        )
    {
#ifdef DEBUG4
        printf("Respecting the opponent will counter specific situation (situation's respect value: %i >= %i)\n", enemyRespect, personality->respectTreshold);
#endif

        // We respect that our opponent will counter our move. So we select their counter (yomi layer 1)
        if (chosenResponse->counterSize)
        {
            situation *enemyChoice;
            int currentSuccessRateAsCounter = -1000;
            int i;

            // Yomi Layer 1
/*            // in case of multiple counters, evaluate what are more likely to be chosen based on successRateAsCounter.
            // todo: make this into a list
            for (i = 0; i < chosenResponse->counterSize; i++)
            {
                if (chosenResponse->counter[i]->successRateAsCounter > currentSuccessRateAsCounter)
                {
                    enemyChoice = chosenResponse->counter[i];
                    currentSuccessRateAsCounter = enemyChoice->successRateAsCounter;
                }
            }*/

            enemyChoice = chosenResponse->counter[0];
            chosenResponse = enemyChoice;

#ifdef DEBUG4   
            printf("Situation for enemy (Yomi layer %i): ", layerNumber);
            debugPrintSituation(enemyChoice->situation, enemyChoice->situationSize);
            printf("\n Move with layer: %i\n", enemyChoice->chosenMove);
#endif

/*            // Now that we have the enemy's yomi layer 1, we look for our counter (Yomi layer 2)
            if (enemyChoice->counterSize)
            {
                // todo: make this into a list
                situation *yomiLayer2 = enemyChoice->counter[0];
            
                chosenResponse = yomiLayer2;
#ifdef DEBUG4   
                printf("Situation for our counter (Yomi Layer %i): ", layerNumber + 1);
                debugPrintSituation(chosenResponse->situation, chosenResponse->situationSize);
                printf("\n Move with layer: %i\n", enemyChoice->chosenMove);
                printf("\n");
#endif
            }*/            
        }
        else
        {
            // we don't know how to react. Normally, the trainer program will cover this, but in case something unexpected happens, we should have a neutral answer (or a safe answer?)
           // todo: implement above algo
#ifdef DEBUG4
            printf("We don't know how to react (we don't have the situation in our database). Do a safe move.\n (Todo) \n");
#endif           
           chosenResponse = db->situations[0];           
           //chosenResponse = null;
        }
    }

    return chosenResponse;
}

situation* applyYomi(database* db, situation* chosenResponse)
{    
    chosenResponse = checkYomiLayer(db, chosenResponse, 1);     // Yomi layer 1
    chosenResponse = checkYomiLayer(db, chosenResponse, 3);     // Yomi layer 3
}

situation* selectSituation(database* db, int currentTurn)
{
    // 1.
    int currentSituationSize;

    int* currentSituation = evaluateCurrentSituation(currentTurn, &currentSituationSize);

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

            bool alreadyConsidered = false;
            int j;
            for (j=0; j< responsesCount; j++)
            {
                //check if response has already been considered
                //possible to happen if we consider counters prior to this turn
                if (possibleResponse == responses[j])
                {
                    alreadyConsidered = true;
                    continue;
                }
            }
            if (alreadyConsidered) continue;
            
            considerResponse = true;
            
            if (possibleResponse->situationSize < 2 && possibleResponse->situationSize >= 0)
            {
                // Neutral situations
                considerResponse = true;
            }
            else if (possibleResponse->rankThisTurn > 0)
            {
                // This can happen in cases where we marked a counter as being valid
                // todo: refactor this so cases like this will be considered when the counter is marked instead
                //       of after
                considerResponse = true;
            }
            else
            {            
                if (possibleResponse->situationSize > currentSituationSize)
                {
                    // This situation can't be considered because it cannot happen under the current situation
                    // (todo: can this be too much prediction? can it be a personality?)
                    considerResponse = false;
                    continue;
                }

                // Roshambo specific scenario check
                int j, k;
                
#ifdef DEBUG2
                //debug to see the comparisions done
                printf("\nComparing the ff situations: \n");
                debugPrintSituation(possibleResponse->situation, possibleResponse->situationSize);
                printf("\n");
                debugPrintSituation(currentSituation, currentSituationSize);
                printf("\n");
#endif

                // If we get a single true, consider it.
                considerResponse = 
                    compareSituation_Equal(possibleResponse, currentSituation, currentSituationSize)
                    ||
                    compareSituation_ToLastTurn(possibleResponse, currentSituation, currentSituationSize);

#ifdef DEBUG2
                if (considerResponse)
                    printf("=Situation considered=\n\n");
#endif
#ifdef DEBUG2_VERBOSE
                if (considerResponse == false)
                    printf("=Situation not considered=\n\n");
#endif
            }
            
            if (considerResponse == true)            
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
#ifdef DEBUG2
        printf("no responses found.");
#endif
        //todo:
        responses[0] = db->situations[0];
    }
   
    //3.
    {        
        if (responsesCount)
        {            
            situation* current = null;

            {
                // Sort by rank
                situation** sortedResponses = (situation**) malloc (sizeof(situation**) * responsesCount);

                int i, sortedIndex = 0;
                int max = 0;
                for (i = 0; i < responsesCount; i++)
                {
                    current = responses[i];

                    if (current->rankThisTurn > max)
                        max = current->rankThisTurn;
                }

                for (; max >= 0; max--)
                {
                    for (i = 0; i < responsesCount; i++)
                    {
                        current = responses[i];
                        if (current->rankThisTurn == max)
                        {
                            sortedResponses[sortedIndex++] = current;
                        }
                    }
                }
                
                responses = sortedResponses;
            }

            {
                // Sort by more defined situations
                situation** sortedResponses = (situation**) malloc (sizeof(situation**) * responsesCount);
                
                int i, sortedIndex = 0;
                int max = 0;
                for (i = 0; i < responsesCount; i++)
                {
                    current = responses[i];

                    if (current->situationSize > max)
                        max = current->situationSize;
                }

                for (; max >= 0; max--)
                {
                    for (i = 0; i < responsesCount; i++)
                    {
                        current = responses[i];
                        if (current->situationSize == max)
                        {
                            sortedResponses[sortedIndex++] = current;
                        }
                    }
                }
                
                responses = sortedResponses;
            }               

            {
                /////////////////////
                // Sort by more successful situations                                
                situation** sortedResponses = (situation**) malloc (sizeof(situation**) * responsesCount);
                int i = 0, j = 0, k = 0;
                int sortedIndex = 0;
                int startpos = 0;
                int previousRank = responses[0]->rankThisTurn;
                
                while (i < responsesCount)
                {
                    // find max successRate
                    int max = 0;
                    for (; i < responsesCount; i++)
                    {
                        current = responses[i];

                        if (current->successRate > max)
                            max = current->successRate;
                        
                        if (previousRank != current->rankThisTurn)
                        {
                            previousRank = current->rankThisTurn;
                            break;
                        }
                    }


                    for (; max >= -100; max--)
                    {
                        for (j = startpos; j < i; j++)
                        {
                            current = responses[j];
                            if (current->successRate == max)
                            {
                                sortedResponses[sortedIndex++] = current;
                            }
                        }
                    }
                    
                    startpos = j;
                }
                    
                responses = sortedResponses;
            }
       
            {
                // remove those with low success rate
                situation** successfulResponses = (situation**) malloc (sizeof(situation**) * responsesCount);
                situation* current = null;

                int i, sortedIndex = 0;
                int max = 0;
                for (i = 0; i < responsesCount; i++)
                {
                    current = responses[i];
                    if (current->successRate >= personality->successRateTreshold)
                    {
                        successfulResponses[sortedIndex++] = current;
                    }
                }
             
                if (sortedIndex > 0)
                {
                    responses = successfulResponses;
                    responsesCount = sortedIndex;
                }
                else    
                {
                    //this means that all the possible responses are actually bad choices (low success rate)
                #ifdef DEBUG3
                    printf("All possible responses have low success rate.\n");
                #endif
                }
            }
        }
    }
    ////////////////////
    
    ////////////////////
    // Sort by etc
    ////////////////////
    
    
    //4.
    situation* chosenResponse = responses[0];
    situation* originalResponse = chosenResponse;
    
#ifdef DEBUG2
    // If debug 2 is enabled, we need to reprint this so we can see it immediately.
    printf("\nsituation for turn #%i is: ", currentTurn);
    debugPrintSituation(currentSituation, currentSituationSize);
    printf("\n\n");
#endif
#ifdef DEBUG4
    printf("Selected situation (prior to applying Yomi): ");
    debugPrintSituation (chosenResponse->situation, chosenResponse->situationSize);
    printf("\n");
#endif
    chosenResponse = applyYomi(db, chosenResponse);
    
#ifdef DEBUG5
    if (chosenResponse == originalResponse)
    {
        printf(" No yomi layer chosen.\n");
    }
    else
    {
        printf("Yomi applied. Final situation: ");
        debugPrintSituation (chosenResponse->situation, chosenResponse->situationSize);
        printf("\n");
    }
    
    printf("\nPossible responses found (sorted):\n");
    int j;
    for (i=0; i< responsesCount; i++)
    {
        printf("response #%i situation: ", i, responses[i]->situationSize);
        debugPrintSituation (responses[i]->situation, responses[i]->situationSize);
        if (originalResponse == responses[i])
            printf(" (chosen) ");
        printf("\n move: %i", responses[i]->chosenMove);
        printf(" respect: %i", responses[i]->enemyRespect);
        printf(" successRate: %i", responses[i]->successRate);
        printf(" rank: %i", responses[i]->rankThisTurn);
        printf("\n");
        printf("\n");
    }
    
    if (originalResponse != chosenResponse)
    {
        for (i=0; i < db->size; i++)
        {
            if (db->situations[i] == chosenResponse)
            {
                printf("\nFinal yomi layer chosen:");
                debugPrintSituation (db->situations[i]->situation, db->situations[i]->situationSize);
                printf("\n");
                break;
            }
        }
    }
#endif

    return chosenResponse;
}

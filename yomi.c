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
#define DEBUG3
#define DEBUG4
#define DEBUG5

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
    currentSituation->counter = (situation**) realloc (currentSituation->counter, sizeof(situation*) * (currentSituation->counterSize + 1));
    currentSituation->counter[currentSituation->counterSize] = foundCounter;
    currentSituation->counterSize++;
}

// Find a situation string in the database and return it.
// todo: its possible to have multiple situations found. return a list
situation* findSituation(database* db, char* Situation, int situationSize)
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
    
    Personality->initialRespectOnOpponent = 100;
    Personality->initialDisrespectOnOpponent = 30;
    Personality->respectModifier = 30;
    Personality->disrespectModifier = 10;
    Personality->respectTreshold = 20;

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
    newSituation = createSituation(db);
    newSituation->chosenMove = rock;

    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
    newSituation->chosenMove = paper;
     
    newSituation = createSituation(db);
    newSituation->chosenMove = scissors;

    // counter situations
    newSituation = createSituation(db);
    newSituation->chosenMove = rock;
    newSituation->situation[0] = scissors;
    newSituation->situationSize = 1;

    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
    newSituation->situation[0] = rock;
    newSituation->situationSize = 1;
     
    newSituation = createSituation(db);
    newSituation->chosenMove = scissors;
    newSituation->situation[0] = paper;
    newSituation->situationSize = 1;

    // test situation:
/*    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
    newSituation->situation[0] = rock;
    newSituation->situation[1] = rock;
    newSituation->situation[2] = paper;
    newSituation->situation[3] = paper;
    newSituation->situation[4] = scissors;
    newSituation->situation[5] = scissors;
    newSituation->situationSize = 6;
*/
    return db;
}

situation* findCounter(database* db, situation *attackingSituation)
{
    int moveToCounterSituation = (attackingSituation->chosenMove + 1) % 3; //todo: roshambo specific.
    int i;

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
        
        // in roshambo, we only need to account for the last move in the situation
        if (currentSituation->situation[currentSituation->situationSize - 1] == attackingSituation->situation[attackingSituation->situationSize - 1])
        {
            //todo: what if we have multiple counters?
            return currentSituation;
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

situation* createOneYomiLayer(database* db, int currentTurn, int layerNumber, situation* previousYomiLayer, char *situationLastTurn, int situationLastTurnSize)
{
    //todo: add wildcard prediction to findcounter
    //situation* newYomiLayer = findCounter(db, yomiLayer1);
    //situation* newYomiLayer = findSituation(db, previousYomiLayer->situation, previousYomiLayer->situationSize);

    situation* newYomiLayer = null;    
    int oppMove = previousYomiLayer->chosenMove;
    if (newYomiLayer == null || previousYomiLayer->chosenMove != oppMove)
    {
#ifdef DEBUG
        printf("\nCreating new situation for yomi layer %i\n", layerNumber);
#endif

        //We did not find this counter situation in our database. Let's make one.
        //copy situation from previous yomi layer and put in this layer but add the prediction flag for player's choice
        newYomiLayer = createSituation(db);
        
        //todo: very roshambo specific.
        newYomiLayer->chosenMove = (oppMove + 1) % 3; 
        
        int i = 0;
        for (i = 0; i < previousYomiLayer->situationSize; i++)
        {
            newYomiLayer->situation[i] = previousYomiLayer->situation[i];
        }
        
        // add the prediction flag on the first yomi layer
        if (layerNumber == 1)
            newYomiLayer->situation[i++] = wildcard;
        
        newYomiLayer->situation[i++] = oppMove;     
        newYomiLayer->situationSize = i;
        newYomiLayer->successRateAsCounter += 50;    //todo: should be personality value

        // layer 1 is an enemy prediction
        if (layerNumber == 1)
            newYomiLayer->enemyRespect = 100;
        
        addCounter(previousYomiLayer, newYomiLayer);
    }
    
#ifdef DEBUG
    printf("Yomi layer %i (", layerNumber);
    debugPrintSituation(newYomiLayer->situation, newYomiLayer->situationSize);
    printf(")\n Chosen move: %i.\n\n", newYomiLayer->chosenMove);
#endif

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
#ifdef DEBUG      
        printf("adding yomi layer %i as counter to yomi layer %i\n", layerNumber, layerNumber - 1);
#endif            
        addCounter(previousYomiLayer, newYomiLayer);
    }
    
    return newYomiLayer;
}

void createYomiLayers(database* db, int currentTurn, situation* currentSituation, int oppMove)
{
    int situationSize;
    int* situationLastTurn = evaluateCurrentSituation(currentTurn - 1, &situationSize);

    situation* yomiLayer0 = findSituation(db, situationLastTurn, situationSize);
    if (yomiLayer0 == null)
    {
#ifdef DEBUG
        printf("new situation found. creating situation for ");
        debugPrintSituation(situationLastTurn , situationSize);
        printf("\n");
#endif

        yomiLayer0 = createSituation(db);
        
        //todo: very roshambo specific.
        yomiLayer0->chosenMove = oppMove; 
        
        int i = 0;
        for (i = 0; i < situationSize; i++)
        {
            yomiLayer0->situation[i] = situationLastTurn[i];
        }
        yomiLayer0->situationSize = situationSize;
    }
    
#ifdef DEBUG
    printf("Yomi layer 0 (");
    debugPrintSituation(yomiLayer0->situation, yomiLayer0->situationSize);
    printf(")\n Chosen move: %i.\n\n", yomiLayer0->chosenMove);
#endif
    
    situation* yomiLayer1 = 
        createOneYomiLayer(db, currentTurn, 1, yomiLayer0, currentSituation, situationSize);
    situation* yomiLayer2 = 
        createOneYomiLayer(db, currentTurn, 2, yomiLayer1, yomiLayer0, situationSize);
    situation* yomiLayer3 = 
        createOneYomiLayer(db, currentTurn, 3, yomiLayer2, yomiLayer1, situationSize);
    situation* yomiLayer4 = 
        createOneYomiLayer(db, currentTurn, 4, yomiLayer3, yomiLayer2, situationSize);     
    
    //yomiLayer5 is the same as layer 1, so we loop this back.
    addCounter(yomiLayer4, yomiLayer1);
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
        printf ("fatal error: this is the first turn but we are already evaluating.");
        return;
    }
   
    if (victory)
    {
        currentSituation->successRate += 10;
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialDisrespectOnOpponent;
        else
            currentSituation->enemyRespect -= personality->disrespectModifier;
    }
    else
    {
        // record the situation in the database where we received a lost.
        currentSituation->successRate -= 10;
        
        if (currentSituation->enemyRespect == UNINITIALIZED_VALUE)
            currentSituation->enemyRespect = personality->initialRespectOnOpponent;
        else
            currentSituation->enemyRespect += personality->respectModifier;

#ifdef DEBUG
        printf("Lost. Updating situation ", currentTurn);
        debugPrintSituation(currentSituation->situation, currentSituation->situationSize);
        printf(":\n");
        printf(" Success rate:%i\n", currentSituation->successRate);
        printf(" Enemy respect value:%i\n", currentSituation->enemyRespect);
#endif

        //todo: this is the training program
        // create a new situation (if none exists) that is the counter to this turn's situation. 
        createYomiLayers(db, currentTurn, currentSituation, oppMove);
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
    
    // Initialize database
/*    if (currentTurn == 0)
        initYomi();
*/
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
    printf("Choice: %i", move);
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
        currentSituation = (char*) malloc (sizeof(int*) * (*currentSituationSize));
                
        j = 0;
        for (i = startTurn; i < maxTurn; i++)
        {
            currentSituation[j+0] = my_history[i + 1];
            currentSituation[j+1] = opp_history[i + 1];
            j+=2;
        }
    }

#ifdef DEBUG
    printf("\nsituation for turn #%i is: ", currentTurn);
    int k;
    for (k = 0; k < *currentSituationSize; k++)
         printf("%i", currentSituation[k]);
    printf("\n");
#endif
    
    return currentSituation;
}

bool compareSituation_Equal(situation* possibleResponse, char* currentSituation, int currentSituationSize)
{
    ////////////////////////////
    // If both situations are equal, it means this situation has already happened before
    ////////////////////////////

    if (possibleResponse->situationSize != currentSituationSize)
        return false;

    int i;
    for (i = 0; i < currentSituationSize; i++)
        if ((possibleResponse->situation[i] != currentSituation[i]) &&
            (possibleResponse->situation[i] != wildcard))
            return false;

#ifdef DEBUG2
    printf("  Both situations are equal\n");
#endif

    possibleResponse->rankThisTurn += 50;

    return true;
}

bool compareSituation_ToLastTurn(situation* possibleResponse, char* currentSituation, int currentSituationSize)
{
    ////////////////////////////
    // Compare to last turn
    ////////////////////////////
       
    // we offset by 2 so we can find the situation tha reflects last turn.
    
    int difference = currentSituationSize - possibleResponse->situationSize;
    if (abs(difference) < 2)
        return false;
        
    bool considerResponse = true;
    int offset = (currentSituationSize - possibleResponse->situationSize) - 2;
    if (offset < 2) offset = 2;

#ifdef DEBUG2
    printf("Checking Last Turn:\n--=\n");
    printf("offset: %i. %i to %i\n", offset, possibleResponse->situationSize, currentSituationSize);
#endif      
    int j,k;
    
    for (j = 0, k = offset; j < possibleResponse->situationSize && k < currentSituationSize; j++, k++)
    {
#ifdef DEBUG2
     printf("%i == ", possibleResponse->situation[j]);
     printf("%i\n", currentSituation[k]);
#endif
        if (possibleResponse->situation[j] != currentSituation[k])
        {
            considerResponse = false;
            break;
        }
    }

    if (considerResponse == true)
    {
#ifdef DEBUG2
        printf("Situation similar to last turn\n");
#endif
        possibleResponse->rankThisTurn += 30;
    }
    
    return considerResponse;
}

situation* checkYomiLayer(database* db, situation* chosenResponse, int passNumber)
{   
    // Check if the Yomi AI should respect the opponent on current situation
    if (chosenResponse->enemyRespect > personality->respectTreshold)
    {
#ifdef DEBUG4
        printf("Respecting the opponent to counter move\n", chosenResponse->counterSize);
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
            enemyChoice = chosenResponse;

            // Now that we have the enemy's yomi layer 1, we look for our counter (Yomi layer 2)
            if (enemyChoice->counterSize)
            {
                // todo: make this into a list
                situation *yomiLayer2 = enemyChoice->counter[0];
            
                chosenResponse = yomiLayer2;
#ifdef DEBUG4   
                int j;
                printf("Situation for enemy (Yomi layer %i): ", passNumber);
                debugPrintSituation(enemyChoice->situation, enemyChoice->situationSize);
                printf("\n");
                
                printf("Situation for our counter (Yomi Layer %i): ", passNumber + 1);
                debugPrintSituation(chosenResponse->situation, chosenResponse->situationSize);
                printf("\n");
                printf(" Chosen move: %i\n", chosenResponse->chosenMove);
#endif
            }
        }
        else
        {
            // we don't know how to react. Normally, the trainer program will cover this, but in case something unexpected happens, we should have a neutral answer (or a safe answer?)
           // todo: implement above algo
           chosenResponse = db->situations[0];           
           //chosenResponse = null;
        }
    }

    return chosenResponse;
}

situation* applyYomi(database* db, situation* chosenResponse)
{    
    chosenResponse = checkYomiLayer(db, chosenResponse, 1);     // Yomi layer 1 - 2
    chosenResponse = checkYomiLayer(db, chosenResponse, 3);     // Yomi layer 3 - 4   
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
            
            // for low success rate scenarios, use the counter
/*            if (possibleResponse->successRate < personality->successRateTreshold)
            {
#ifdef DEBUG2
            printf("Response situation: ", possibleResponse->successRate, possibleResponse->chosenMove);
            int i;
            for (i = 0; i < possibleResponse->situationSize; i++)
                 printf("%i", possibleResponse->situation[i]);
            printf(" has low successrate (%i).", possibleResponse->successRate, possibleResponse->chosenMove);
            printf("\n");
#endif
                if (possibleResponse->counterSize)
                {
#ifdef DEBUG2
                    printf("%i counters found\n", possibleResponse->counterSize);
#endif

                    //todo: some situations have multiple counters. consider them as well
                    possibleResponse = possibleResponse->counter[0];
                    
#ifdef DEBUG2
                    printf("Adding counters:\n");
                    
                    int i;
                    printf(" Counter move: %i Situation:", possibleResponse->chosenMove);
                    for (i = 0; i < possibleResponse->situationSize; i++)
                         printf("%i", possibleResponse->situation[i]);
                    printf("\n");
#endif                
                }
            }            
*/
            if (possibleResponse->situationSize < 2 && possibleResponse->situationSize >= 0)
            {
                // Neutral situations
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
                printf("=Situation considered=\n\n");
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
        printf("no responses found.");getch();
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
        
        // find max rankThisTurn
        int i, j = 0;
        int max = 0;
        for (i = 0; i < responsesCount; i++)
        {
            current = tempResponses[i];

            if (current->rankThisTurn > max)
                max = current->rankThisTurn;
        }

        for (; max >= 0; max--)
        {
            for (i = 0; i < responsesCount; i++)
            {
                current = tempResponses[i];
                if (current->rankThisTurn == max)
                {
                    sortedResponses[j++] = current;
                }
            }
        }
        
        responses = sortedResponses;
    }
    ////////////////////
    
    ////////////////////
    // Sort by etc
    ////////////////////
    
    
    //4.
    situation* chosenResponse = responses[0];
    situation* originalResponse = chosenResponse;
    
    chosenResponse = applyYomi(db, chosenResponse);
    
#ifdef DEBUG
    debugPrintSituation (chosenResponse->situation, chosenResponse->situationSize);
    printf("\nPossible responses found (sorted): %i\n", responsesCount);
    int j;
    for (i=0; i< responsesCount; i++)
    {
        printf("response #%i situation:", i, responses[i]->situationSize);
        debugPrintSituation (responses[i]->situation, responses[i]->situationSize);
        if (originalResponse == responses[i])
            printf(" (chosen) ");
        printf("\nmove: %i", responses[i]->chosenMove);
        printf(" respect: %i", responses[i]->enemyRespect);
        printf(" successRate: %i", responses[i]->successRate);
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

// RoShamBo Tournament Test Suite structures

#define rock        0
#define paper       1
#define scissors    2
//wildcard is ? and is an unknown element or a prediction flag
#define wildcard    -1

extern int my_history[];
extern int opp_history[];

#define null            0
#define maxYomiLayer    3

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
char* evaluateCurrentSituation(int currentTurn, int* currentSituationSize);

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
                return iterSituation;
        }
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

void debugPrintSituation(char* situation, int size)
{
#ifdef DEBUG
    int i;
    for (i = 0; i < size; i++)
        printf("%i", situation[i]);
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
    newSituation = createSituation(db);
    newSituation->chosenMove = paper;
    newSituation->situation[0] = rock;
    newSituation->situation[1] = rock;
    newSituation->situation[2] = paper;
    newSituation->situation[3] = paper;
    newSituation->situation[4] = scissors;
    newSituation->situation[5] = scissors;
    newSituation->situationSize = 6;

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
const int True = 1;
const int False = 0;

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
        
        int situationSize;
        char* situationLastTurn = evaluateCurrentSituation(currentTurn - 1, &situationSize);
        situation* yomiLayer1 = findSituation(db, situationLastTurn, situationSize);
        int i;

        //todo: check each yomiLayer1 situation and see if the move that the enemy played this turn is there
        //      if not, create a new situation with the opponent's point of view
        if (yomiLayer1 == null || yomiLayer1->chosenMove != oppMove)
        {
#ifdef DEBUG
            printf("\nCreating new situation for yomi layer 1\n");
#endif
        
            // create new situation
            yomiLayer1 = createSituation(db);
            yomiLayer1->chosenMove = oppMove;
 
            for (i = 0; i < situationSize; i++)
            {
                yomiLayer1->situation[i] = situationLastTurn[i];
            }
            yomiLayer1->situationSize = situationSize;

            yomiLayer1->successRateAsCounter += 50;    //todo: should be personality value

            addCounter(currentSituation, yomiLayer1);
        }

#ifdef DEBUG
        printf("Yomi layer 1 (");
        debugPrintSituation(yomiLayer1->situation, yomiLayer1->situationSize);
        printf("):\n Chosen move: %i.\n", yomiLayer1->chosenMove);
#endif
    
        //todo: add wildcard prediction to findcountersituation* yomiLayer2 = findCounter(db, yomiLayer1);
        situation* yomiLayer2 = null;
        
        if (yomiLayer2 == null)
        {
#ifdef DEBUG
            printf("\nCreating new situation for yomi layer 2\n");
#endif

            // We did not find this counter situation in our database. Let's make one.
            //copy situation from YomiLayer1 and put in layer2 but add the prediction flag for player's choice
            yomiLayer2 = createSituation(db);
            yomiLayer2->chosenMove = (oppMove + 1) % 3; //todo: very roshambo specific.

            i = 0;
            for (i = 0; i < situationSize; i++)
            {
                yomiLayer2->situation[i] = situationLastTurn[i];
            }
            
            // add the prediction flag
            yomiLayer2->situation[i++] = wildcard;
            yomiLayer2->situation[i++] = oppMove;     
            yomiLayer2->situationSize = i;
            yomiLayer2->successRateAsCounter += 50;    //todo: should be personality value
            
            addCounter(yomiLayer1, yomiLayer2);
        }
        
#ifdef DEBUG
        printf("Yomi layer 2 (");
        debugPrintSituation(yomiLayer2->situation, yomiLayer2->situationSize);
        printf(")\n Chosen move: %i.\n\n", yomiLayer2->chosenMove);
#endif

        //check if yomiLayer1 has yomiLayer2 as its counter. If not, add it
        bool isInCounterList = False;
        for (i = 0; i < yomiLayer1->counterSize; i++)
        {
            if (yomiLayer1->counter[i] == yomiLayer2)
            {
                isInCounterList = True;
                break;
            }
        }
        
        if (isInCounterList == False)
        {
#ifdef DEBUG      
            printf("adding yomi layer 2 as counter to yomi layer 1");
#endif            
            addCounter(yomiLayer1, yomiLayer2);
        }

//////////////////
/*        
        int size = 0;
        char* situationData = evaluateCurrentSituation(currentTurn, &size);

        situation* foundCounter = null;
        int i, j;

        for (i = 0; i < db->size; i++)
        {
#ifdef DEBUG
            printf(".%i %i.", size, db->situations[i]->situationSize);
#endif
            if (size != db->situations[i]->situationSize)
                continue;

            char *compare = db->situations[i]->situation;
            for (j = 0; j < size; j++)
                if (compare != situationData[i])
                {
#ifdef DEBUG
                    printf("%i %i\n", compare, situationData[i]);
#endif
                    continue;
                }
            // we found a situation that is the same as the current situation
#ifdef DEBUG
            printf("we found a situation that is the same as the current situation\n");
#endif
            foundCounter = db->situations[i];
            break;
        }

        if (foundCounter == null)
        {
            // situation not found in database. add it.
#ifdef DEBUG
            printf("situation not found in database. add it.");
#endif        
            foundCounter = createSituation(db);
        }
        
        foundCounter->successRateAsCounter = 50;    //todo: should be personality value
        foundCounter->chosenMove = -1;
        addCounter(currentSituation, foundCounter);
         
#ifdef DEBUG
        printf("\nnew situation created for:");
        for (i = 0; i < size; i++)
        {
            foundCounter->situation[i] = situationData[i];
            printf("%i", situationData[i]);
        }
        foundCounter->situationSize = size;       
        printf("\n");
#endif        
        // what beats this situation?
        // todo: send this to the training program?
        for (i = 0; i < db->size; i++)
        {
            situation *currentSituation = db->situations[i];
            
            // we only check neutral moves
            if (currentSituation->situationSize > 2)
            {
#ifdef DEBUG
                printf("skipping move: %i\n", currentSituation->chosenMove);
#endif
                continue;
            }         
            
            // in roshambo, we only need to account for the last move in the situation
            if (currentSituation->situation[currentSituation->situationSize - 1] == foundCounter->situation[foundCounter->situationSize - 1])
            {
                //todo: its possible to have multiple counters in the other games
                foundCounter->chosenMove = (oppMove + 1) % 3; //todo: very roshambo specific.
                
#ifdef DEBUG
                printf("For this situation, use counter: %i\n", foundCounter->chosenMove);
#endif

                break;
            }
        }
        
        if (foundCounter->chosenMove == -1)
        {
            printf("\nNo counter found for losing situation!\n");
            getch();
        }
*/        
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

char* evaluateCurrentSituation(int currentTurn, int* currentSituationSize)
{
    char* currentSituation = null;

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
        currentSituation = (char*) malloc (sizeof(char*) * (*currentSituationSize));
                
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

#ifdef DEBUG2
    printf("checking if both situations are equal\n");
#endif
    if (possibleResponse->situationSize != currentSituationSize)
        return False;

    int i;
    for (i = 0; i < currentSituationSize; i+=2)
        if (possibleResponse->situation[i] != currentSituation[i])
            return False;

#ifdef DEBUG2
    printf("equal situations found\n");
#endif

    possibleResponse->rankThisTurn += 50;

    return True;
}

bool compareSituation_ToLastTurn(situation* possibleResponse, char* currentSituation, int currentSituationSize)
{
    ////////////////////////////
    // Compare to last turn
    ////////////////////////////
       
    // we offset by 2 so we can find the situation tha reflects last turn.
    
    int difference = currentSituationSize - possibleResponse->situationSize;
    if (abs(difference) < 2)
        return False;
    
    
    bool considerResponse = True;
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
            considerResponse = False;
#ifdef DEBUG2
            printf("Don't consider\n");
#endif                        
            break;
        }
    }

    if (considerResponse == True)
    {
#ifdef DEBUG2
        printf("Consider\n");
    printf("--=\n");
#endif
        possibleResponse->rankThisTurn += 30;
    }
    
    return considerResponse;
}

situation* applyYomi(database* db, situation* chosenResponse)
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

            // Now that we have the enemy's yomi layer 1, we look for our counter (Yomi layer 2)
            if (enemyChoice->counterSize)
            {
                // todo: make this into a list
                situation *yomiLayer2 = enemyChoice->counter[0];
            
                chosenResponse = yomiLayer2;
#ifdef DEBUG4   
                int j;
                printf("Situation for enemy (Yomi layer 1): \n");
                for (j = 0; j < enemyChoice->situationSize; j++)
                    printf("%i", enemyChoice->situation[j]);
                printf("\n");
                
                printf("Situation for our counter (Yomi Layer 2): \n");
                for (j = 0; j < chosenResponse->situationSize; j++)
                    printf("%i", chosenResponse->situation[j]);
                printf("\n");
                printf(" Chosen move: %i\n", chosenResponse->chosenMove);
                getch();//*/
#endif

                // evaluate the likely responses and see if we need to go to the Yomi Layer 3.
                // todo: implement yomi layer 3 and 4
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

situation* selectSituation(database* db, int currentTurn)
{
    // 1.
    int currentSituationSize;

    char* currentSituation = evaluateCurrentSituation(currentTurn, &currentSituationSize);

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

            bool alreadyConsidered = False;
            int j;
            for (j=0; j< responsesCount; j++)
            {
                //check if response has already been considered
                //possible to happen if we consider counters prior to this turn
                if (possibleResponse == responses[j])
                {
                    alreadyConsidered = True;
                    continue;
                }
            }
            if (alreadyConsidered) continue;
            
            considerResponse = True;
            
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
                considerResponse = True;
            }
            else
            {            
                if (possibleResponse->situationSize > currentSituationSize)
                {
                    // This situation can't be considered because it cannot happen under the current situation
                    // (todo: can this be too much prediction? can it be a personality?)
                    considerResponse = False;
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
                printf("\n");//*/
#endif

                // If we get a single True, consider it.
                considerResponse = 
                    compareSituation_Equal(possibleResponse, currentSituation, currentSituationSize)
                    ||
                    compareSituation_ToLastTurn(possibleResponse, currentSituation, currentSituationSize);
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

    chosenResponse = applyYomi(db, chosenResponse);
    
#ifdef DEBUG
    if (responsesCount > 1)
    {
//          printf ("%i responses found", responsesCount);getch();
    }
    /* debug
*/    printf("\nPossible responses found (sorted): %i\n", responsesCount);
    int j;
    for (i=0; i< responsesCount; i++)
    {
        printf("response #%i situation:", i, responses[i]->situationSize);
        for (j = 0; j < responses[i]->situationSize; j++)
        {
            printf("%i",responses[i]->situation[j]);
        }
        if (chosenResponse == responses[i])
            printf(" (chosen) ");
        printf("\nmove: %i", responses[i]->chosenMove);
        printf(" respect: %i", responses[i]->enemyRespect);
        printf(" successRate: %i", responses[i]->successRate);
        printf("\n");
    }
#endif

    return chosenResponse;
}

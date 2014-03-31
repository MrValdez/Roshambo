// emphasis that its an improvement of beat frequent pick
// tally results from original beat frequent pick
// (lower is better in scatter plot)

extern int my_history[];
extern int opp_history[];

extern int yomiVariable1;

void BestFrequentPick()
{
   //return (biased_roshambo (1/3.0f, 1/3.0f) + 1) % 3;
    static int statR = 0;
    static int statP = 0;
    static int statS = 0;
    int targetTurn = yomiVariable1;
    static int denominator;
    static float rockProb;
    static float paperProb;
    static float targetRock;
    static float targetPaper;
    int currentTurn = my_history[0]; // number of games

    if (currentTurn == 0)
    {
        statR = 0;
        statP = 0;
        statS = 0;
        denominator = targetTurn;
        rockProb = 1/3.0f;
        paperProb = 1/3.0f;
        targetRock = rockProb * targetTurn;
        targetPaper = paperProb * targetTurn;
        return biased_roshambo (1/3.0f, 1/3.0f);
    }
    
    int oppMove = opp_history[currentTurn];
    
    if (oppMove == 0)
        statR ++;
    if (oppMove == 1)
        statP ++;
    if (oppMove == 2)
        statS ++;

    if (denominator <= 0)
    {
        rockProb = statR / (float) currentTurn;
        paperProb = statP / (float) currentTurn;
        
        targetRock = rockProb * (currentTurn + targetTurn);
        targetPaper = paperProb * (currentTurn + targetTurn);
        
        denominator = targetTurn;
    }
        
    float thisTurnRockProb = (targetRock - statR) / (float) (denominator);
    float thisTurnPaperProb = (targetPaper - statP) / (float) (denominator);
        
    if (thisTurnRockProb <= 0 || thisTurnPaperProb <= 0 || thisTurnRockProb + thisTurnPaperProb >= 1.0f)
    {
        rockProb = statR / (float) currentTurn;
        paperProb = statP / (float) currentTurn;
        
        targetRock = rockProb * (currentTurn + targetTurn);
        targetPaper = paperProb * (currentTurn + targetTurn);
        
        denominator = targetTurn;

        thisTurnRockProb = (targetRock - statR) / (float) denominator;
        thisTurnPaperProb = (targetPaper - statP) / (float) denominator;
    }    

    thisTurnRockProb = thisTurnRockProb < 0 ? 0 : thisTurnRockProb; 
    thisTurnPaperProb = thisTurnPaperProb < 0 ? 0 : thisTurnPaperProb; 
     /*    printf("statR, targetRock: %i %f\n ", statR, targetRock);
    printf("denominator: %i  \n", denominator);
    printf("thisTurnRockProb, thisTurnPaperProb: %f %f\n\n", thisTurnRockProb, thisTurnPaperProb);getch();
   */
    denominator--;
    return (biased_roshambo (thisTurnRockProb, thisTurnPaperProb) + 1) % 3;
}
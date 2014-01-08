
/*  RoShamBo Tournament Sample Program     Darse Billings,  Oct 1999  */
/*                                                                    */
/*  This program may be used and modified freely, as long as the      */
/*  original author credit is maintained.  There are no guarantees    */
/*  of any kind.  Use at your own risk.                               */
/*                                                                    */
/*  Compile with the math library:  gcc rsb-ts1.c -lm                 */
/*                                                                    */
/*  Check the main web page for future versions of this program:      */
/*                                                                    */
/*        http://www.cs.ualberta.ca/~darse/rsbpc.html                 */

/*  this version contains corrections to the table driven dummy bots  */
/*  (thanks to Michael Callahan for noticing this)  -drb 07/00        */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#include <malloc.h>
#include <assert.h>
#include <sys/time.h>
#include <unistd.h>

#define rock      0
#define paper     1
#define scissors  2

#define players   18         /* number of players in the tournament */
#define trials    1000       /* number of turns per match */
#define tourneys  1          /* number of round-robin tournaments */
#define drawn     50         /* +/- statistical draw range */
                             /* for 1000 trials rec: 50.6 / sqrt(tourneys) */

#define fw        4          /* field width for printed numbers */
#define verbose1  0          /* print result of each trial */
#define verbose2  0          /* print match histories */
#define verbose3  1          /* print result of each match */

/*  Full History Structure (global variables, accessible to the
                            current player during each match)

      - element 0 is the number of trials played so far
      - element i is the action taken on turn i (1 <= i <= trials ) */

int my_history[trials+1], opp_history[trials+1];

/*  Tournament Crosstable Structure  */

#define nameleng  18
typedef struct {
    char name[nameleng+1];   /* descriptive name (max 18 chars) */
    int(*pname)();           /* function name for computer player */
    int result[players+1];   /* list of player's match results */
} Player_Table;


#define maxrandom 2147483648.0   /* 2^31, ratio range is 0 <= r < 1 */

int flip_biased_coin (double prob)
{
    /* flip an unfair coin (bit) with given probability of getting a 1 */

    if ( (random() / maxrandom) >= prob )
         return(0);
    else return(1);
}

int biased_roshambo (double prob_rock, double prob_paper)
{
    /* roshambo with given probabilities of rock, paper, or scissors */
    double throw;

    throw = random() / maxrandom;

    if ( throw < prob_rock )                   { return(rock); }
    else if ( throw < prob_rock + prob_paper ) { return(paper); }
    else /* throw >= prob_rock + prob_paper */ { return(scissors); }
}

/*  Index of RoShamBo Player Algorithms:

 Rank  Dummy Bot         Open BoB  Leng      -max  level history use

  27 * Random (Optimal)   32  19     1       [-0]    L0  h0
   - * Good Ole Rock       -   -     1       [-1000] L0  h0
   - * R-P-S 20-20-60      -   -     1       [-1000] L0  h0
   - * Rotate R-P-S        -   -     1       [-1000] L0  h0
   - * Beat Last Move      -   -     1       [-1000] L1 oh1
   - * Always Switchin'    -   -     3       [-500]  L0 mh1
   - * Beat Frequent Pick  -   -    11       [-1000] L1 oh1
    
  21 * Pi                 31   9     5       [-1000] L0  h0
  49 * Switch A Lot       45  49     3       [-320]  L0 mh1
  40 * Flat               40  44    16       [-420]  L0 mh1
   - * Anti-Flat           -   -    16       [-1000] L1 oh1
  32 * Foxtrot            36  22     4       [-500]  L0 mh1
  16 * De Bruijn          28   3     5       [-500]  L0  h0
  46 * Text               41  52     5       [-ukn]  L0  h0
  29 * Anti-rotn          22  32    40       [-40]   L1 oh2 +fail-safe
  45 * Copy-drift         39  50     9       [-500]  L0 oh1
  48 * Add-react          43  51     9       [-800]  L0 bh1 +gear-shifting
  42 * Add-drift          38  47     9       [-500]  L0 bh1

 Rank Entrant           Open BoB  Leng Nat  Author

   1  Iocaine Powder      1   1   134  USA  Dan Egnor
   2  Phasenbott          2   2    99  USA  Jakob Mandelson
   3  MegaHAL             3   7   149  Aus  Jason Hutchens
   4  RussRocker4         4   8   120  USA  Russ Williams
   5  Biopic              6   6    80  Can  Jonathan Schaeffer
   7  Simple Modeller     7  13   135   UK  Don Beal
  14  Simple Predictor    9  21    63   UK  Don Beal
   8  Robertot            8  12    53  Ger  Andreas Junghanns
  10  Boom               10  18   208  Net  Jack van Rijswijk
  11  Shofar             17  11    98  USA  Rudi Cilibrasi
  13  ACT-R Lag2         15  14    20  USA  Dan Bothell, C Lebiere, R West
  15  Majikthise         25   5    62  Can  Markian Hlynka
  18  Vroomfondel        24  10    62  Can  Markian Hlynka
  17  Granite            11  23    97  Can  Aaron Davidson
  19  Marble             12  24    95  Can  Aaron Davidson
  22  ZQ Bot             16  26    99  Can  Neil Burch
  24  Sweet Rocky        18  30    36  Mex  Lourdes Pena
  25  Piedra             19  31    23  Mex  Lourdes Pena
  28  Mixed Strategy     23  29    53   UK  Thad Frogley
  38  Multi-strategy     42  38    86  Can  Mark James
  44  Inocencio          48  37    95   UK  Rafael Morales
  50  Peterbot           53  42    43  USA  Peter Baylie
  12  Bugbrain           14  15    51  Can  Sunir Shah
  52  Knucklehead        49  48    30  Can  Sunir Shah

  --  Psychic Friends Network      47  USA  Michael Schatz, F Hill, TJ Walls
      (Unofficial Super-Modified Class, i.e. it cheats)
*/

/*  Dummy Bots  (written by Darse Billings)  */

int randbot ()  /* Random (Optimal) */
{
    /* generate action uniformly at random (optimal strategy) */
    return( random() % 3);
}

int rockbot ()  /* Good Ole Rock */
{
    /* "Good ole rock.  Nuthin' beats rock." */
    return(rock);
}

int r226bot ()  /* R-P-S 20-20-60 */
{
    /* play 20% rock, 20% paper, 60% scissors */
    return( biased_roshambo(0.2, 0.2));
}

int rotatebot ()  /* Rotate R-P-S */
{
    /* rotate choice each turn r -> p -> s */
    return( my_history[0] % 3);
}

int copybot ()  /* Beat Last Move */
{
    /* do whatever would have beat the opponent last turn */
    return( (opp_history[opp_history[0]] + 1) % 3);
}

int switchbot ()  /* Always Switchin' */
{
    /* never repeat the previous pick */
    if ( my_history[my_history[0]] == rock ) {
        return( biased_roshambo(0.0, 0.5) ); }
    else if ( my_history[my_history[0]] == paper ) {
        return( biased_roshambo(0.5, 0.0) ); }
    else return( biased_roshambo(0.5, 0.5) );
}

int freqbot ()  /* Beat Frequent Pick */
{
    /* beat the opponent's most frequent choice */

    int i, rcount, pcount, scount;

    rcount = 0;  pcount = 0;  scount = 0;
    for (i = 1; i <= opp_history[0]; i++) {
        if (opp_history[i] == rock)            { rcount++; }
        else if (opp_history[i] == paper)      { pcount++; }
        else /* opp_history[i] == scissors */  { scount++; }
    }
    if ( (rcount > pcount) && (rcount > scount) ) { return(paper); }
    else if ( pcount > scount ) { return(scissors); }
    else { return(rock); }
}

int freqbot2 ()  /* Beat Frequent Pick (again) */
{
    /* maintain stats with static variables to avoid re-scanning
       the history array  (based on code by Don Beal) */

    static int rcount, pcount, scount;
    int opp_last;

    if( opp_history[0] == 0 ) {
        rcount = 0;  pcount = 0;  scount = 0;  }
    else {
      opp_last = opp_history[opp_history[0]];
      if ( opp_last == rock)          { rcount++; }
      else if ( opp_last == paper)    { pcount++; }
      else /* opp_last == scissors */ { scount++; }
    }
    if ( (rcount > pcount) && (rcount > scount) ) { return(paper); }
    else if ( pcount > scount ) { return(scissors); }
    else { return(rock); }
}

int pibot ()  /* Pi bot */
{
    /* base each decision on a digit of pi (skipping 0s) */

    static int index;
    static int pi_table [1200] =  /* skipping 0s leaves 1088 digits */
{3,1,4,1,5,9,2,6,5,3,5,8,9,7,9,3,2,3,8,4,6,2,6,4,3,3,8,3,2,7,9,5,0,2,8,8,4,1,9,7,
 1,6,9,3,9,9,3,7,5,1,0,5,8,2,0,9,7,4,9,4,4,5,9,2,3,0,7,8,1,6,4,0,6,2,8,6,2,0,8,9,
 9,8,6,2,8,0,3,4,8,2,5,3,4,2,1,1,7,0,6,7,9,8,2,1,4,8,0,8,6,5,1,3,2,8,2,3,0,6,6,4,
 7,0,9,3,8,4,4,6,0,9,5,5,0,5,8,2,2,3,1,7,2,5,3,5,9,4,0,8,1,2,8,4,8,1,1,1,7,4,5,0,
 2,8,4,1,0,2,7,0,1,9,3,8,5,2,1,1,0,5,5,5,9,6,4,4,6,2,2,9,4,8,9,5,4,9,3,0,3,8,1,9,
 6,4,4,2,8,8,1,0,9,7,5,6,6,5,9,3,3,4,4,6,1,2,8,4,7,5,6,4,8,2,3,3,7,8,6,7,8,3,1,6,
 5,2,7,1,2,0,1,9,0,9,1,4,5,6,4,8,5,6,6,9,2,3,4,6,0,3,4,8,6,1,0,4,5,4,3,2,6,6,4,8,
 2,1,3,3,9,3,6,0,7,2,6,0,2,4,9,1,4,1,2,7,3,7,2,4,5,8,7,0,0,6,6,0,6,3,1,5,5,8,8,1,
 7,4,8,8,1,5,2,0,9,2,0,9,6,2,8,2,9,2,5,4,0,9,1,7,1,5,3,6,4,3,6,7,8,9,2,5,9,0,3,6,
 0,0,1,1,3,3,0,5,3,0,5,4,8,8,2,0,4,6,6,5,2,1,3,8,4,1,4,6,9,5,1,9,4,1,5,1,1,6,0,9,
 4,3,3,0,5,7,2,7,0,3,6,5,7,5,9,5,9,1,9,5,3,0,9,2,1,8,6,1,1,7,3,8,1,9,3,2,6,1,1,7,
 9,3,1,0,5,1,1,8,5,4,8,0,7,4,4,6,2,3,7,9,9,6,2,7,4,9,5,6,7,3,5,1,8,8,5,7,5,2,7,2,
 4,8,9,1,2,2,7,9,3,8,1,8,3,0,1,1,9,4,9,1,2,9,8,3,3,6,7,3,3,6,2,4,4,0,6,5,6,6,4,3,
 0,8,6,0,2,1,3,9,4,9,4,6,3,9,5,2,2,4,7,3,7,1,9,0,7,0,2,1,7,9,8,6,0,9,4,3,7,0,2,7,
 7,0,5,3,9,2,1,7,1,7,6,2,9,3,1,7,6,7,5,2,3,8,4,6,7,4,8,1,8,4,6,7,6,6,9,4,0,5,1,3,
 2,0,0,0,5,6,8,1,2,7,1,4,5,2,6,3,5,6,0,8,2,7,7,8,5,7,7,1,3,4,2,7,5,7,7,8,9,6,0,9,
 1,7,3,6,3,7,1,7,8,7,2,1,4,6,8,4,4,0,9,0,1,2,2,4,9,5,3,4,3,0,1,4,6,5,4,9,5,8,5,3,
 7,1,0,5,0,7,9,2,2,7,9,6,8,9,2,5,8,9,2,3,5,4,2,0,1,9,9,5,6,1,1,2,1,2,9,0,2,1,9,6,
 0,8,6,4,0,3,4,4,1,8,1,5,9,8,1,3,6,2,9,7,7,4,7,7,1,3,0,9,9,6,0,5,1,8,7,0,7,2,1,1,
 3,4,9,9,9,9,9,9,8,3,7,2,9,7,8,0,4,9,9,5,1,0,5,9,7,3,1,7,3,2,8,1,6,0,9,6,3,1,8,5,
 9,5,0,2,4,4,5,9,4,5,5,3,4,6,9,0,8,3,0,2,6,4,2,5,2,2,3,0,8,2,5,3,3,4,4,6,8,5,0,3,
 5,2,6,1,9,3,1,1,8,8,1,7,1,0,1,0,0,0,3,1,3,7,8,3,8,7,5,2,8,8,6,5,8,7,5,3,3,2,0,8,
 3,8,1,4,2,0,6,1,7,1,7,7,6,6,9,1,4,7,3,0,3,5,9,8,2,5,3,4,9,0,4,2,8,7,5,5,4,6,8,7,
 3,1,1,5,9,5,6,2,8,6,3,8,8,2,3,5,3,7,8,7,5,9,3,7,5,1,9,5,7,7,8,1,8,5,7,7,8,0,5,3,
 2,1,7,1,2,2,6,8,0,6,6,1,3,0,0,1,9,2,7,8,7,6,6,1,1,1,9,5,9,0,9,2,1,6,4,2,0,1,9,8,
 9,3,8,0,9,5,2,5,7,2,0,1,0,6,5,4,8,5,8,6,3,2,7,8,8,6,5,9,3,6,1,5,3,3,8,1,8,2,7,9,
 6,8,2,3,0,3,0,1,9,5,2,0,3,5,3,0,1,8,5,2,9,6,8,9,9,5,7,7,3,6,2,2,5,9,9,4,1,3,8,9,
 1,2,4,9,7,2,1,7,7,5,2,8,3,4,7,9,1,3,1,5,1,5,5,7,4,8,5,7,2,4,2,4,5,4,1,5,0,6,9,5,
 9,5,0,8,2,9,5,3,3,1,1,6,8,6,1,7,2,7,8,5,5,8,8,9,0,7,5,0,9,8,3,8,1,7,5,4,6,3,7,4,
 6,4,9,3,9,3,1,9,2,5,5,0,6,0,4,0,0,9,2,7,7,0,1,6,7,1,1,3,9,0,0,9,8,4,8,8,2,4,0,1};

    /* corrected code courtesy of Michael Callahan */
    if (my_history[0] == 0) { index = 0; }
    else {
        index = (index + 1) % 1200;
	while (pi_table[index] == 0) { index++; }
	/* Don't have to check over 1200 again because last entry is not 0. */
    }
    return(pi_table[index] % 3);
}

int switchalot ()  /* Switch A Lot */
{
    /* seldom repeat the previous pick */
    if ( my_history[my_history[0]] == rock ) {
        return( biased_roshambo(0.12, 0.44) ); }
    else if ( my_history[my_history[0]] == paper ) {
        return( biased_roshambo(0.44, 0.12) ); }
    else return( biased_roshambo(0.44, 0.44) );
}

int flatbot3 ()  /* Flat bot */
{
    /* flat distribution, 20% chance of most frequent actions */
    static int rc, pc, sc;
    int mylm, choice;

    choice = 0;
    if ( my_history[0] == 0 ) {
        rc = 0; pc = 0; sc = 0; }
    else {
        mylm = my_history[my_history[0]];
        if (mylm == rock)            { rc++; }
        else if (mylm == paper)      { pc++; }
        else /* mylm == scissors */  { sc++; }
    }
    if ((rc < pc) && (rc < sc)) {
        choice = biased_roshambo(0.8, 0.1); }
    if ((pc < rc) && (pc < sc)) {
        choice = biased_roshambo(0.1, 0.8); }
    if ((sc < rc) && (sc < pc)) {
        choice = biased_roshambo(0.1, 0.1); }
    if ((rc == pc) && (rc < sc)) {
        choice = biased_roshambo(0.45, 0.45); }
    if ((rc == sc) && (rc < pc)) {
        choice = biased_roshambo(0.45, 0.1); }
    if ((pc == sc) && (pc < rc)) {
        choice = biased_roshambo(0.1, 0.45); }
    if ((rc == pc) && (rc == sc)) {
        choice = random() % 3; }
    /* printf("[%d %d %d: %d]", rc, pc, sc, choice); */
    return(choice);
}

int antiflatbot ()  /* Anti-Flat bot */
{
    /* maximally exploit flat distribution */

    static int rc, pc, sc;
    int opplm, choice;

    choice = 0;
    if ( opp_history[0] == 0 ) {
        rc = 0; pc = 0; sc = 0; }
    else {
        opplm = opp_history[opp_history[0]];
        if (opplm == rock)           { rc++; }
        else if (opplm == paper)      { pc++; }
        else /* opplm == scissors */  { sc++; }
    }
    if ((rc < pc) && (rc < sc)) {
        choice = paper; }
    if ((pc < rc) && (pc < sc)) {
        choice = scissors; }
    if ((sc < rc) && (sc < pc)) {
        choice = rock; }
    if ((rc == pc) && (rc < sc)) {
        choice = paper; }
    if ((rc == sc) && (rc < pc)) {
        choice = rock; }
    if ((pc == sc) && (pc < rc)) {
        choice = scissors; }
    if ((rc == pc) && (rc == sc)) {
        choice = random() % 3; }
    /* printf("[%d %d %d: %d]", rc, pc, sc, choice); */
    return(choice);
}

int foxtrotbot ()  /* Foxtrot bot */
{
    /* set pattern: rand prev+2 rand prev+1 rand prev+0, repeat */

    int turn;

    turn = my_history[0] + 1;

    if ( turn % 2 ) {
        return( random() % 3 ); }
    else {
        return( (my_history[turn-1] + turn) % 3 ); }
}

int debruijn81 ()  /* De Bruijn string */
{
    /* several De Bruijn strings of length 81 concatentated */

    static int db_table [1000] = /* De Bruijn sequence: */
{1,0,2,0,0,2,0,2,0,1,1,0,0,2,2,1,0,0,1,1,2,2,0,0,1,2,1,0,2,2,2,2,0,1,2,0,2,2,0,2,
 1,1,2,1,1,0,1,1,1,2,0,0,0,0,2,1,0,1,0,1,2,2,1,2,0,1,0,0,0,1,0,2,1,2,1,2,2,2,1,1,
 1,0,0,1,1,1,1,0,1,0,2,2,2,0,0,2,2,0,2,0,1,0,1,1,0,2,1,1,2,2,2,2,1,1,1,2,0,1,2,2,
 1,2,0,0,0,1,0,0,0,0,2,0,2,2,1,0,0,1,2,1,2,2,0,1,1,2,1,1,0,0,2,1,0,1,2,0,2,1,2,1,
 0,2,1,1,2,0,0,1,0,1,2,2,0,1,0,0,2,0,1,2,0,1,1,2,1,1,1,1,0,2,0,2,1,0,2,2,0,2,2,2,
 2,0,0,0,1,2,1,2,2,2,1,1,0,1,1,0,0,0,0,2,1,2,0,2,0,0,2,2,1,0,0,1,1,1,2,2,1,2,1,0,
 1,0,2,1,0,1,0,2,0,2,0,0,1,2,2,2,0,2,1,0,0,1,1,1,2,2,1,1,0,2,2,0,0,0,2,2,2,2,1,2,
 2,0,1,2,0,0,2,0,1,1,2,1,2,1,1,1,1,0,0,2,1,2,0,1,0,0,0,0,1,0,1,1,0,1,2,1,0,2,1,1,
 2,0,2,2,2,2,1,1,1,1,0,0,2,0,2,2,2,1,2,1,0,2,1,0,0,0,0,2,1,1,2,2,1,0,1,0,0,1,1,1,
 2,1,1,0,1,2,2,2,2,0,0,1,2,0,2,0,1,2,1,2,0,1,0,1,1,2,0,0,0,1,0,2,2,0,2,1,2,2,0,1,
 1,0,2,0,0,0,0,0,0,1,0,0,0,2,1,1,0,0,1,1,1,1,0,2,0,2,1,2,0,2,2,1,2,2,2,1,1,1,2,1,
 2,1,0,0,2,0,1,1,0,1,0,2,1,0,2,2,2,2,0,2,0,0,2,2,0,0,1,2,2,1,0,1,1,2,0,1,2,1,1,2,
 2,0,1,0,1,2,2,2,0,2,0,0,2,0,2,1,2,2,2,2,0,0,0,0,2,2,1,0,0,0,1,2,0,1,2,1,2,0,0,1,
 0,2,0,1,0,0,2,1,0,1,2,2,1,1,2,0,2,2,2,1,2,1,0,2,2,0,1,1,0,2,1,1,0,0,1,1,2,1,1,1,
 1,0,1,0,1,1,1,1,1,1,2,1,0,0,0,0,1,1,0,2,1,2,1,2,2,2,0,0,1,2,0,1,0,1,2,1,1,2,2,0,
 2,0,2,1,1,0,0,1,0,2,0,0,2,0,1,1,2,0,2,2,1,1,1,1,0,1,0,0,2,2,2,2,1,2,0,0,0,2,1,0,
 2,2,0,1,2,2,1,0,2,1,0,1,0,1,1,1,1,2,1,1,0,1,2,1,2,2,2,2,1,2,0,0,0,1,1,2,0,2,0,2,
 1,0,0,0,0,2,0,0,1,0,0,2,2,2,0,0,2,1,1,2,2,0,1,2,0,1,1,0,0,1,2,2,1,1,1,0,2,0,1,0,
 2,2,0,2,2,1,0,2,1,2,2,2,1,0,1,0,2,2,1,2,0,2,1,0,2,0,0,0,0,1,2,1,0,0,2,0,2,2,0,1,
 0,1,1,2,1,1,0,0,1,0,0,0,2,1,1,2,0,0,2,2,2,2,0,0,1,1,1,0,2,1,2,1,2,2,1,1,1,1,2,2,
 0,2,0,1,2,0,1,1,0,1,1,0,0,1,1,0,1,2,0,1,2,1,2,2,1,0,0,2,0,2,1,0,1,0,2,2,0,1,1,2,
 1,0,2,0,0,1,0,1,1,1,2,2,2,2,1,2,0,2,2,1,1,2,0,0,2,1,2,1,1,1,1,0,2,1,1,0,0,0,0,2,
 2,2,0,0,0,1,2,2,0,2,0,2,2,0,2,1,1,2,0,2,0,0,1,1,1,0,0,1,2,1,1,0,1,1,0,2,2,0,0,2,
 2,1,1,1,1,2,1,2,1,0,2,0,2,2,2,2,1,2,0,0,0,1,0,0,2,1,0,0,0,0,2,0,1,1,2,2,2,0,1,2,
 2,1,0,1,0,1,2,0,1,0,2,1,0,2,0,2,1,1,1,0,0,2,2,2,0,1,1,2,2,1,2,0,0,0,1,0,1,2,1,0};

    /* corrected code courtesy of Michael Callahan */
    return(db_table[my_history[0] % 1000]);
}

int textbot ()  /* Text bot */
{
    /* English text (rsbpc post) converted to r-p-s */
    /* contains:  281 0's, 267 1's, 452 2's (heavy bias) */

    static int db_table [1000] = 
{2,0,2,2,2,1,0,0,1,2,2,1,2,2,2,0,2,1,2,0,0,2,1,0,2,1,0,2,2,1,1,0,0,2,2,0,0,1,0,1,
 1,1,0,2,1,2,1,0,1,1,2,2,0,2,0,0,2,2,2,0,1,1,1,0,1,1,2,0,0,0,2,2,2,1,2,1,0,0,1,0,
 1,1,2,2,0,2,1,0,1,1,2,1,0,0,2,0,2,1,1,2,0,0,2,0,0,1,1,0,0,1,2,2,1,2,1,2,2,2,2,2,
 0,2,0,2,2,2,0,2,1,0,1,1,2,0,2,2,1,2,2,0,1,2,2,2,0,0,1,1,2,2,0,2,0,0,2,2,1,1,1,0,
 2,1,2,2,0,2,2,2,0,2,1,0,0,1,0,1,1,1,1,2,2,2,0,0,1,0,1,2,1,2,0,0,2,2,1,1,2,2,0,0,
 2,2,2,1,2,1,2,1,1,1,2,2,2,0,2,1,0,2,2,1,0,1,2,2,2,0,2,1,1,2,2,1,0,2,2,1,1,0,0,2,
 1,1,0,1,0,2,2,2,0,2,2,2,1,1,2,1,0,0,2,0,2,1,1,2,0,0,2,0,0,1,1,0,0,1,2,2,0,1,2,1,
 2,1,0,1,1,0,2,2,1,1,1,2,2,2,2,0,2,2,2,2,2,2,2,2,1,2,2,1,2,0,1,2,2,1,1,2,0,1,2,2,
 2,2,0,0,1,2,2,2,0,0,2,2,2,0,0,1,1,0,0,0,1,2,2,1,2,2,2,2,2,2,1,0,1,1,0,2,1,2,1,1,
 1,0,2,1,2,2,0,1,0,0,0,2,0,2,2,0,1,1,0,2,2,2,2,1,2,1,1,0,0,2,2,1,1,2,2,0,1,1,2,1,
 1,2,1,2,2,0,2,2,2,1,1,1,2,2,0,1,2,1,0,1,1,2,1,2,2,2,2,2,2,2,2,2,2,2,0,2,1,0,1,1,
 2,0,1,1,2,2,1,2,2,2,1,0,2,2,2,0,0,2,2,2,2,2,2,2,1,0,1,1,2,0,1,2,1,0,1,0,0,2,1,2,
 2,0,0,1,0,1,2,0,2,0,0,1,2,2,0,2,2,2,0,0,2,1,0,0,0,2,1,2,2,1,1,1,1,2,0,1,2,2,0,0,
 2,1,1,0,0,1,1,0,0,1,1,1,2,2,1,0,2,2,2,2,1,2,0,2,0,0,1,2,2,2,2,2,2,1,1,1,2,2,0,2,
 2,1,2,2,2,2,2,2,0,2,1,0,0,2,2,0,1,2,1,2,2,0,2,2,2,0,2,2,2,0,2,0,1,2,2,1,1,1,2,0,
 2,0,0,1,2,0,1,2,0,0,0,2,2,2,1,0,0,1,1,0,0,1,2,0,0,2,1,2,1,1,1,2,0,2,2,0,0,2,0,0,
 0,2,2,0,0,0,1,2,2,1,2,1,0,0,1,1,0,0,1,1,2,2,2,2,1,1,2,0,2,2,0,0,2,1,0,1,2,1,2,0,
 0,2,1,2,1,2,0,0,2,1,2,0,0,2,2,0,0,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,0,2,1,0,1,1,
 2,0,1,1,2,2,0,2,2,2,1,1,1,2,2,0,1,2,2,0,0,1,0,1,0,2,0,0,0,1,2,1,2,1,1,1,2,0,2,2,
 2,0,0,2,2,0,0,2,1,0,0,2,2,2,0,0,2,1,0,2,2,1,2,2,0,2,2,2,0,1,2,0,1,1,0,2,1,0,0,2,
 1,2,1,2,0,1,2,2,1,1,2,0,1,2,2,0,2,0,2,0,0,1,2,2,1,2,2,1,0,2,0,0,2,2,0,2,0,0,0,0,
 1,0,1,2,1,2,2,0,1,2,1,0,1,2,1,0,2,2,0,2,2,0,0,1,2,1,0,0,2,1,2,0,0,0,2,1,2,0,0,2,
 2,1,0,2,2,1,2,2,0,2,0,1,2,2,0,0,0,2,2,2,1,0,0,2,2,1,2,2,0,2,1,2,0,2,1,2,2,2,0,2,
 1,0,0,2,2,0,2,2,2,2,2,2,0,0,2,1,2,0,0,2,2,2,0,2,1,1,0,1,0,2,1,1,2,0,0,2,2,0,2,2,
 1,2,0,0,2,1,2,1,0,0,2,2,0,2,2,2,2,1,2,0,2,2,2,2,2,2,0,1,1,0,2,2,2,2,2,0,1,1,2,2};

    /* corrected code courtesy of Michael Callahan */
    return(db_table[my_history[0] % 1000]);
}

int antirotnbot ()  /* Anti-rotn bot */
{
    /* observes rotations in opponent's sequence,
       exploits max or min, whichever difference is greater */

    /* crude implementation, could be simplified */

    static int no, up, dn, score;
    int mv, diff, diff2, small, med, large;

    mv = opp_history[0];
    if (mv == 0) {
        no = 0; up = 0; dn = 0; score = 0;
    }
    else {
        diff = (my_history[mv] - opp_history[mv] + 3) % 3;
        if ( diff == 1 ) { score++; }
        if ( diff == 2 ) { score--; }
        if (mv > 1) {
            diff = (opp_history[mv] - opp_history[mv-1] + 3) % 3;
            if (diff == 0) { no++; }
            if (diff == 1) { up++; }
            if (diff == 2) { dn++; }
        }
    }

    /* fail-safe at 4% of match length */
    if ( score < -trials/25 ) {
        return(random() % 3); }

    if ((no == up) && (no == dn)) {
        return(random() % 3); }

    /* sort */
    if ((no <= up) && (no <= dn)) {
        small = no;
        if (up <= dn) { med = up; large = dn; }
        else { med = dn; large = up; }
    }
    else if (up <= dn) {
        small = up;
        if (no <= dn) { med = no; large = dn; }
        else { med = dn; large = no; }
    }
    else {
        small = dn;
        if (no <= up) { med = no; large = up; }
        else { med = up; large = no; }
    }

    diff = med - small;    diff2 = large - med;

    if (diff < diff2) { /* clear maximum */
        if ((no > up) && (no > dn)) {
            return((opp_history[opp_history[0]] + 1) % 3); }
        if ((up > no) && (up > dn)) {
            return((opp_history[opp_history[0]] + 2) % 3); }
        if ((dn > no) && (dn > up)) {
            return(opp_history[opp_history[0]]); }
    }
    else if (diff > diff2) { /* clear minimum */
        if ((dn < up) && (dn < no)) {
            return((opp_history[opp_history[0]] + 1) % 3); }
        if ((up < dn) && (up < no)) {
            return(opp_history[opp_history[0]]); }
        if ((no < dn) && (no < up)) {
            return((opp_history[opp_history[0]] + 2) % 3); }
    }
    else if (diff == diff2) {
        if ((no > up) && (up > dn)) {
            return((opp_history[opp_history[0]] + 1) % 3); }
        if ((dn > up) && (up > no)) {
            if (flip_biased_coin(0.5)) {
                return(opp_history[opp_history[0]]); }
            else { return((opp_history[opp_history[0]] + 2) % 3); }
        }
        if ((dn > no) && (no > up)) {
            return(opp_history[opp_history[0]]); }
        if ((up > no) && (no > dn)) {
            if (flip_biased_coin(0.5)) {
                return((opp_history[opp_history[0]] + 1) % 3); }
            else { return((opp_history[opp_history[0]] + 2) % 3); }
        }
        if ((up > dn) && (dn > no)) {
            return((opp_history[opp_history[0]] + 2) % 3); }
        if ((no > dn) && (dn > up)) {
            if (flip_biased_coin(0.5)) {
                return(opp_history[opp_history[0]]); }
            else { return((opp_history[opp_history[0]] + 1) % 3); }
        }
    }
    printf("Error in antirotnbot decision tree!\n");
    return(0);
}

int driftbot ()  /* Copy-drift bot */
{
    /* bias decision by opponent's last move, but drift over time */
    /* max -EV = -0.50 ppt */

    static int gear;
    int mv, throw;

    mv = my_history[0];
    if (mv == 0) { 
        gear = 0;
        throw = random() % 3; }
    else {
        if (flip_biased_coin(0.5)) {    
            throw = opp_history[mv]; }
        else { throw = random() % 3; }
        if ( mv % 111 == 0 ) {
            gear += 2; }
    }
    return((throw + gear) % 3);
}

int addshiftbot3 ()  /* Add-react bot */
{
    /* base on sum of previous pair (my & opp), shift if losing */
    /* deterministic 80% of the time, thus max -EV = -0.800 ppt */

    static int gear, recent, score;
    int mv, diff;

    mv = my_history[0];
    if (mv == 0) {
        gear = 0; recent = 0; score = 0;
        return( random() % 3 );
    }
    else {
        diff = (my_history[mv] - opp_history[mv] + 3) % 3;
        if ( diff == 1 ) { score++; }
        if ( diff == 2 ) { score--; }
        recent++;
    }

    if (((recent <= 20) && (score <= -3)) ||
        ((recent >  20) && (score <= -recent/10))) {
        /* printf("switching gears at turn %d (%d / %d)\n", mv, score, recent); */
        gear += 2;
        recent = 0;
        score = 0;
    }
    if ( flip_biased_coin(0.2) ) {
        return( random() % 3 ); }
    else {
        return((my_history[mv] + opp_history[mv] + gear) % 3);
    }
}

int adddriftbot2 ()  /* Add-drift bot */
{
    /* base on sum of previous pair (my & opp), drift over time */
    /* deterministic 50% of the time, thus max -EV = -0.500 ppt */

    static int gear;
    int mv;

    mv = my_history[0];
    if (mv == 0) {
        gear = 0;
        return( random() % 3 );
    }
    else if ( mv % 200 == 0 ) { gear += 2; }

    if ( flip_biased_coin(0.5) ) {
        return( random() % 3 ); }
    else {
        return((my_history[mv] + opp_history[mv] + gear) % 3);
    }
}

/*  End of RoShamBo Player Algorithms  */


void Init_Player_Table (Player_Table crosstable[players+1])
{
    int i, j;

    i = 0;  /* list of players in the tournament */
    strcpy(crosstable[i].name, "Player Name");

#ifdef Comment_Block  /* use these to comment out a block of players */

#endif /* end of Comment_Block -- be sure to change the #define players value */

    i++;  /* choose uniformly at random */
    strcpy(crosstable[i].name, "* Random (Optimal)");
    crosstable[i].pname = randbot;

    i++;  /* nuthin' beats rock */
    strcpy(crosstable[i].name, "Good Ole Rock");
    crosstable[i].pname = rockbot;

    i++;  /* 20% rock, 20% paper, 60% scissors, randomly */
    strcpy(crosstable[i].name, "R-P-S 20-20-60");
    crosstable[i].pname = r226bot;

    i++;  /* rotate r -> p -> s */
    strcpy(crosstable[i].name, "Rotate R-P-S");
    crosstable[i].pname = rotatebot;

    i++;  /* beat opponent's last move */
    strcpy(crosstable[i].name, "Beat The Last Move");
    crosstable[i].pname = copybot;

    i++;  /* never repeat the same move */
    strcpy(crosstable[i].name, "Always Switchin'");
    crosstable[i].pname = switchbot;

    i++;  /* beat the most frequent opponent choice */
    strcpy(crosstable[i].name, "Beat Frequent Pick");
    crosstable[i].pname = freqbot2;

    i++;  /* choose according to the digits of Pi */
    strcpy(crosstable[i].name, "* Pi");
    crosstable[i].pname = pibot;

    i++;  /* repeat last play infrequently */
    strcpy(crosstable[i].name, "* Switch A Lot");
    crosstable[i].pname = switchalot;

    i++;  /* flatter than normal distribution (cf human) */
    strcpy(crosstable[i].name, "* Flat");
    crosstable[i].pname = flatbot3;

    i++;  /* beat flat distributions */
    strcpy(crosstable[i].name, "* Anti-Flat");
    crosstable[i].pname = antiflatbot;

    i++;  /* foxtrot sequence: rand +2 rand +1 rand +0 */
    strcpy(crosstable[i].name, "* Foxtrot");
    crosstable[i].pname = foxtrotbot;

    i++;  /* De Bruijn sequences of length 81 */
    strcpy(crosstable[i].name, "* De Bruijn");
    crosstable[i].pname = debruijn81;

    i++;  /* English text (rsbpc post) */
    strcpy(crosstable[i].name, "* Text");
    crosstable[i].pname = textbot;

    i++;  /* exploit most common rotation (min or max) */
    strcpy(crosstable[i].name, "* Anti-rotn");
    crosstable[i].pname = antirotnbot;

    i++;  /* copy opponent; shift gears every 111 turns */
    strcpy(crosstable[i].name, "* Copy-drift");
    crosstable[i].pname = driftbot;

    i++;  /* add prev pair of moves; shift gears if losing (-3 or -10%) */
    strcpy(crosstable[i].name, "* Add-react");
    crosstable[i].pname = addshiftbot3;

    i++;  /* add prev pair of moves; drift over time (200) */
    strcpy(crosstable[i].name, "* Add-drift");
    crosstable[i].pname = adddriftbot2;

    for (i = 0; i <= players; i++) {
      for (j = 0; j <= players; j++) {
        crosstable[i].result[j] = 0;
      }
    }
}

int Play_Match ( int(*player1)(), int(*player2)() )
{
    /* play a match between two RoShamBo players */

    int i, j, p1, p2, p1total, p2total, ties;
    int p1hist[trials+1], p2hist[trials+1];

    p1total = 0; p2total = 0; ties = 0;

    for (i = 0; i <= trials; i++) {
        p1hist[i] = 0; p2hist[i] = 0;
        my_history[i] = 0; opp_history[i] = 0;
    }

    for (i = 1; i <= trials; i++) {

        /* provide copies of history arrays for each player */
        memcpy(my_history, p1hist, sizeof(int)*(trials+1));
        memcpy(opp_history, p2hist, sizeof(int)*(trials+1));

        p1 = player1 ();              /* get player1 action */
        if ( (p1 < 0) || (p1 > 2) ) {
            printf("Error: return value out of range.\n");
            p1 = (p1 % 3 + 3) % 3;    /* note: -5 % 3 = -2, not 1 */
        }

        memcpy(opp_history, p1hist, sizeof(int)*(trials+1));
        memcpy(my_history, p2hist, sizeof(int)*(trials+1));

        p2 = player2 ();             /* get player2 action */
        if ( (p2 < 0) || (p2 > 2) ) {
            printf("Error: return value out of range.\n");
            p2 = (p2 % 3 + 3) % 3;
        }

        p1hist[0]++; p1hist[p1hist[0]] = p1;
        p2hist[0]++; p2hist[p2hist[0]] = p2;

        if (verbose1) { printf(" p1 = %d, p2 = %d", p1, p2); }
        if (p1 == p2) {
            ties++;
            if (verbose1) { printf(" tie!\n"); } }
        else if ( (p1-p2 == 1) || (p1-p2 == -2) ) {
            p1total++;
            if (verbose1) { printf(" p1 wins!\n"); } }
        else if ( (p2-p1 == 1) || (p2-p1 == -2) ) {
            p2total++;
            if (verbose1) { printf(" p2 wins!\n"); } }
        else printf("Error: should not be reached.\n");
    }
    if (verbose2) {
        printf(" Full history of p1 (%d trials):\n", p1hist[0]);
        for (j = 1; j <= trials; j++) {
            printf(" %d", p1hist[j]); }
        printf("\n");
        printf(" Full history of p2 (%d trials):\n", p1hist[0]);
        for (j = 1; j <= trials; j++) {
            printf(" %d", p2hist[j]); }
        printf("\n");
    }
    if (verbose3) {
        printf(" Match: %*d (%*d+ %*d- %*d=)\n", fw, p1total-p2total,
                            fw-1, p1total, fw-1, p2total, fw-1, ties);
    }

    return (p1total - p2total);
}

void Print_T_Results (Player_Table crosstable[players+1])
{
    int i, j;

    printf("\n Tournament results: \n\n");
    printf("    ");
    printf("%-*s ", nameleng, crosstable[0].name);
    printf("  total ");
    for (j = 1; j <= players; j++) {
        printf(" %*d", fw, j);
    }
    printf("\n");
    for (i = 1; i <= players; i++) {
        printf(" %2d ", i);
        printf("%-*s ", nameleng, crosstable[i].name);
        printf(" %*d ", fw+2, crosstable[i].result[0]);
        for (j = 1; j <= players; j++) {
            printf(" %*d", fw, crosstable[i].result[j]);
        }
        printf("\n");
    }
    printf("\n");
}

void Print_Sorted_Results (Player_Table crosstable[players+1])
{
    int i, j, max, swap;
    char nameswap[nameleng+1];

    Player_Table sorted[players+1];

    for (i = 0; i <= players; i++) {
        strcpy(sorted[i].name, crosstable[i].name);
        for (j = 0; j <= players; j++) {
            sorted[i].result[j] = crosstable[i].result[j];
        }
    }

    for (i = 1; i <= players; i++) {
        max = i;
        for (j = i; j <= players; j++) {
            if ( (sorted[j].result[0] > sorted[max].result[0]) ) {
                max = j;
            }
        }
        strcpy(nameswap, sorted[i].name);
        strcpy(sorted[i].name, sorted[max].name);
        strcpy(sorted[max].name, nameswap);
        for (j = 0; j <= players; j++) {
            swap = sorted[i].result[j];
            sorted[i].result[j] = sorted[max].result[j];
            sorted[max].result[j] = swap;
        }
        for (j = 1; j <= players; j++) {
            swap = sorted[j].result[i];
            sorted[j].result[i] = sorted[j].result[max];
            sorted[j].result[max] = swap;
        }
    }
    Print_T_Results (sorted);
}

void Print_Scaled_Results (Player_Table crosstable[players+1])
{
    int i, j, N;

    Player_Table stable[players+1];

    for (i = 0; i <= players; i++) {
        strcpy(stable[i].name, crosstable[i].name);
        for (j = 0; j <= players; j++) {
            stable[i].result[j] = crosstable[i].result[j];
        }
    }

    /* scale down set of N tournaments */
    N = tourneys;
    for (i = 1; i <= players; i++) {
        for (j = 0; j <= players; j++) {
            if ( stable[i].result[j] >= 0 ) {
                stable[i].result[j] = (stable[i].result[j] * 2 + N) / (2*N);
            }
            else {
                stable[i].result[j] = (stable[i].result[j] * 2 - N) / (2*N);
            }
        }
    }
    Print_Sorted_Results (stable);
}

void Print_M_Results (Player_Table crosstable[players+1])
{
    int i, j, win, draw, loss;

    printf("\n Match results: \n\n");
    printf("    ");
    printf("%-*s ", nameleng, crosstable[0].name);
    printf("   total  W  L  D ");
    for (j = 1; j <= players; j++) {
        printf(" %*d", fw-2, j);
    }
    printf("\n");
    for (i = 1; i <= players; i++) {
        printf(" %2d ", i);
        printf("%-*s ", nameleng, crosstable[i].name);
        printf(" %*d ", fw+2, crosstable[i].result[0]);
        win = 0; loss = 0; draw = -1;
        for (j = 1; j <= players; j++) {
            if ( crosstable[i].result[j] == 2 ) { win++; }
            if ( crosstable[i].result[j] == 0 ) { loss++; }
            if ( crosstable[i].result[j] == 1 ) { draw++; }
        }
        printf(" %2d %2d %2d ", win, loss, draw);
        for (j = 1; j <= players; j++) {
            printf(" %*d", fw-2, crosstable[i].result[j]);
        }
        printf("\n");
    }
    printf("\n");
}

void Print_MSorted_Results (Player_Table crosstable[players+1])
{
    int i, j, max, swap;
    char nameswap[nameleng+1];

    Player_Table sorted[players+1];

    for (i = 0; i <= players; i++) {
        strcpy(sorted[i].name, crosstable[i].name);
        for (j = 0; j <= players; j++) {
            sorted[i].result[j] = crosstable[i].result[j];
        }
    }

    for (i = 1; i <= players; i++) {
        max = i;
        for (j = i; j <= players; j++) {
            if ( (sorted[j].result[0] > sorted[max].result[0]) ) {
                max = j;
            }
        }
        strcpy(nameswap, sorted[i].name);
        strcpy(sorted[i].name, sorted[max].name);
        strcpy(sorted[max].name, nameswap);
        for (j = 0; j <= players; j++) {
            swap = sorted[i].result[j];
            sorted[i].result[j] = sorted[max].result[j];
            sorted[max].result[j] = swap;
        }
        for (j = 1; j <= players; j++) {
            swap = sorted[j].result[i];
            sorted[j].result[i] = sorted[j].result[max];
            sorted[j].result[max] = swap;
        }
    }
    Print_M_Results (sorted);
}

void Print_Match_Results (Player_Table crosstable[players+1])
{
    int i, j, N;

    Player_Table mtable[players+1];

    for (i = 0; i <= players; i++) {
        strcpy(mtable[i].name, crosstable[i].name);
        for (j = 0; j <= players; j++) {
            mtable[i].result[j] = crosstable[i].result[j];
        }
    }

    /* scale down set of N tournaments */
    N = tourneys;
    for (i = 1; i <= players; i++) {
        for (j = 0; j <= players; j++) {
            if ( mtable[i].result[j] >= 0 ) {
                mtable[i].result[j] = (mtable[i].result[j] * 2 + N) / (2*N);
            }
            else {
                mtable[i].result[j] = (mtable[i].result[j] * 2 - N) / (2*N);
            }
        }
    }
    /* Print_T_Results (mtable); */ /* scaled results */

    for (i = 1; i <= players; i++) {
        mtable[i].result[0] = -1;  /* account for "draw" vs self */
        for (j = 1; j <= players; j++) {
            if ( mtable[i].result[j] > drawn ) {
                mtable[i].result[j] = 2;
                mtable[i].result[0] += 2;
            }
            else if ( mtable[i].result[j] < -drawn ) {
                mtable[i].result[j] = 0;
            }
            else {
                mtable[i].result[j] = 1;
                mtable[i].result[0] += 1;
            }
        }
    }
    Print_MSorted_Results (mtable);
}

void Play_Tournament (Player_Table crosstable[players+1])
{
    int i, j, score;

    for (i = 1; i <= players; i++) {
        for (j = i+1; j <= players; j++) {
            if (verbose3) { printf(" %-*s vs %-*s ", nameleng,
                crosstable[i].name, nameleng, crosstable[j].name); }
            score = Play_Match (crosstable[i].pname, crosstable[j].pname);
            crosstable[i].result[j] += score;
            crosstable[j].result[i] -= score;
        }
    }

    for (i = 1; i <= players; i++) {
        crosstable[i].result[0] = 0;
        for (j = 1; j <= players; j++) {
            crosstable[i].result[0] += crosstable[i].result[j];
        }
    }
    if (verbose2) { Print_T_Results (crosstable); }
}

int main() {

    int i;
    Player_Table crosstable[players+1];

    /* fixed or variable seed to the random() function */
    /* srandom(time(0)); */
    srandom(0);

    Init_Player_Table (crosstable);

    printf(" Playing %d tournaments with %d trials per match...\n\n",
             tourneys, trials);

    for (i = 1; i <= tourneys; i++) {
        Play_Tournament (crosstable);
    }
    Print_Scaled_Results (crosstable);
    Print_Match_Results (crosstable);
    return(0);
}

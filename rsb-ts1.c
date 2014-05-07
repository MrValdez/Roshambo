
/*  First RoShamBo Tournament Test Suite   Darse Billings,  Oct 1999  */
/*                                                 revised July 2000  */
/*                                                                    */
/*  This program may be used and modified freely, as long as the      */
/*  original author credit is maintained.  There are no guarantees    */
/*  of any kind.                                                      */
/*                                                                    */
/*  The RoShamBo player algorithms contained in this test suite have  */
/*  been generously donated by their authors.  Entries for future     */
/*  RoShamBo competitions may be based on these ideas, but credit     */
/*  must be given to the original author.  Any entry deemed to be     */
/*  too similar to an uncredited existing program will be rejected    */
/*  without further consideration.                                    */
/*                                                                    */
/*  I am pleased to say that _all_ of the top contenders have been    */
/*  released (except for RoShamBot, which is proprietary, and not     */
/*  the author's to give).                                            */
/*                                                                    */
/*  Compile with the math library:  gcc rsb-ts1.c -lm                 */
/*                                                                    */
/*  Check the main web page for future versions of this program:      */
/*                                                                    */
/*        http://www.cs.ualberta.ca/~darse/rsbpc.html                 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#include <assert.h>
#include <sys/time.h>
#include <unistd.h>

#define rock      0
#define paper     1
#define scissors  2

//#define players   42         /* number of players in the tournament */
#define tourneys  1          /* number of round-robin tournaments */
#define trials    1000       /* number of turns per match */

//#define fw        4          /* field width for printed numbers */
int verbose1 = 1;          /* print result of each trial */
int verbose2 = 0;          /* print match histories */
int verbose3 = 1;          /* print result of each match */
int verbose4 = 1;          /* print the tournament result */

// My Changes
#define players   30         /* number of players in the tournament */
#define fw        4          /* field width for printed numbers */
int usePython = 1;

/*  Full History Structure (global variables, accessible to the
                            current player during each match)

      - element 0 is the number of trials played so far
      - element i is the action taken on turn i (1 <= i <= trials ) */

int my_history[trials+1], opp_history[trials+1];

int g_drawn;  /* statistical match draw value (global) */ 
              /* for 1000 turn matches:  50.6 / sqrt(tourneys) */

/*  Tournament Crosstable Structure  */

#define nameleng  18
typedef struct {
   char name[nameleng+1];   /* descriptive name (max 18 chars) */
   int(*pname)();           /* function name for computer player */
   int result[players+1];   /* list of player's match results */
} Player_Table;

#define maxrandom 2147483648.0   /* 2^31, ratio range is 0 <= r < 1 */

//********************************BUG FIXXXXXXX
#undef maxrandom
//#define maxrandom ((float) RAND_MAX )
#define maxrandom 32767.0

long random()
{
  return rand();
}
void bzero(short int *foo, int size)
{
  memset(foo, 0, size);
}
void srandom(unsigned int seed)
{
  return srand(seed);
}
//************************************

extern int yomi();
extern int python();

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
   
   /*//printf("\n %f %f %f %i", prob_rock, prob_paper, throw, RAND_MAX ); 
   prob_rock = ((int)(prob_rock * 1000)) / 1000.0f;
   prob_paper = ((int)(prob_paper * 1000)) / 1000.0f;
   printf("\n%f", throw );
   printf("\n %f %f %f %i", prob_rock, prob_paper, throw, RAND_MAX ); 
   //getch();*/   

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
   if ( turn % 2 ) { return( random() % 3 ); }
   else { return( (my_history[turn-1] + turn) % 3 ); }
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
/**********************************************************************/


/*  Entrant:  Iocaine Powder (1)   Dan Egnor (USA)

    Winner of the First International RoShamBo Programming Competition

 Iocaine Powder             (from: http://ofb.net/~egnor/iocaine.html)

 They were both poisoned.
 
 Iocaine Powder is a heuristically designed compilation of strategies and
 meta-strategies, entered in Darse Billings' excellent First International
 RoShamBo Programming Competition. You may use its source code freely; I
 ask only that you give me credit for any derived works. I attempt here to
 explain how it works.
 
 Meta-Strategy
 
 RoShamBo strategies attempt to predict what the opponent will do. Given a
 successful prediction, it is easy to defeat the opponent (if you know they
 will play rock, you play paper). However, straightforward prediction will
 often fail; the opponent may not be vulnerable to prediction, or worse, they
 might have anticipated your predictive logic and played accordingly. Iocaine
 Powder's meta-strategy expands any predictive algorithm P into six possible
 strategies:
 
 P.0: naive application
      Assume the opponent is vulnerable to prediction by P; predict their
      next move, and play to beat it. If P predicts your opponent will play
      rock, play paper to cover rock. This is the obvious application of P.
 
 P.1: defeat second-guessing
      Assume the opponent thinks you will use P.0. If P predicts rock, P.0
      would play paper to cover rock, but the opponent could anticipate this
      move and play scissors to cut paper. Instead, you play rock to dull
      scissors.
 
 P.2: defeat triple-guessing
      Assume the opponent thinks you will use P.1. Your opponent thinks you
      will play rock to dull the scissors they would have played to cut the
      paper you would have played to cover the rock P would have predicted,
      so they will play paper to cover your rock. But you one-up them,
      playing scissors to cut their paper.
 
      At this point, you should be getting weary of the endless chain. "We
      could second-guess each other forever," you say. But no; because of the
      nature of RoShamBo, P.3 recommends you play paper -- just like P.0! So
      we're only left with these three strategies, each of which will suggest
      a different alternative. (This may not seem useful to you, but have
      patience.)
 
 P'.0: second-guess the opponent
      This strategy assumes the opponent uses P themselves against you.
      Modify P (if necessary) to exchange the position of you and your
      opponent. If P' predicts that you will play rock, you would expect
      your opponent to play paper, but instead you play scissors.
 
 P'.1, P'.2: variations on a theme
      As with P.1 and P.2, these represent "rotations" of the basic idea,
      designed to counteract your opponent's second-guessing.
 
 So, for even a single predictive algorithm P, we now have six possible
 strategies. One of them may be correct -- but that's little more useful
 than saying "one of rock, scissors, or paper will be the correct next
 move". We need a meta-strategy to decide between these six strategies.
 
 Iocaine Powder's basic meta-strategy is simple: Use past performance to
 judge future results.
 
 The basic assumption made by this meta-strategy is that an opponent will not
 quickly vary their strategy. Either they will play some predictive algorithm
 P, or they will play to defeat it, or use some level of second-guessing; but
 whatever they do, they will do it consistently. To take advantage of this
 (assumed) predictability, at every round Iocaine Powder measures how well
 each of the strategies under consideration (six for every predictive
 algorithm!)  would have done, if it had played them. It assigns each one a
 score, using the standard scoring scheme used by the tournament: +1 point if
 the strategy would have won the hand, -1 if it would have lost, 0 if it
 would have drawn.
 
 Then, to actually choose a move, Iocaine Powder simply picks the strategy
 variant with the highest score to date.
 
 The end result is that, for any given predictive technique, we will beat any
 contestant that would be beaten by the technique, any contestant using the
 technique directly, and any contestant designed to defeat the technique
 directly.
 
 Strategies
 
 All the meta-strategy in the world isn't useful without some predictive
 algorithms. Iocaine Powder uses three predictors:
 
 Random guess
      This "predictor" simply chooses a move at random. I include this
      algorithm as a hedge; if someone is actually able to predict and defeat
      Iocaine Powder with any regularity, before long the random predictor
      will be ranked with the highest score (since nobody can defeat
      random!). At that point, the meta-strategy will ensure that the program
      "cuts its losses" and starts playing randomly to avoid a devastating
      loss. (Thanks to Jesse Rosenstock for discovering the necessity of such
      a hedge.)
 
 Frequency analysis
      The frequency analyzer looks at the opponent's history, finds the move
      they have made most frequently in the past, and predicts that they will
      choose it. While this scores a resounding defeat again "Good Ole Rock",
      it isn't very useful against more sophisticated opponents (which are
      usually quite symmetrical). I include it mostly to defeat other
      competitors which use it as a predictive algorithm.
 
 History matching
      This is easily the strongest predictor in Iocaine Powder's arsenal, and
      variants of this technique are widely used in other strong entries. The
      version in Iocaine Powder looks for a sequence in the past matching the
      last few moves. For example, if in the last three moves, we played
      paper against rock, scissors against scissors, and scissors against
      rock, the predictor will look for times in the past when the same three
      moves occurred. (In fact, it looks for the longest match to recent
      history; a repeat of the last 30 moves is considered better than just
      the last 3 moves.) Once such a repeat is located, the history matcher
      examines the move our opponent made afterwards, and assumes they will
      make it again. (Thanks to Rudi Cilibrasi for introducing me to this
      algorithm, long ago.)
 
      Once history is established, this predictor easily defeats many weak
      contestants. Perhaps more importantly, the application of meta-strategy
      allows Iocaine to outguess other strong opponents.
 
 Details
 
 If you look at Iocaine Powder's source code, you'll discover additional
 features which I haven't treated in this simplified explanation. For
 example, the strategy arsenal includes several variations of frequency
 analysis and history matching, each of which looks at a different amount of
 history; in some cases, prediction using the last 5 moves is superior to
 prediction using the last 500. We run each algorithm with history sizes of
 1000, 100, 10, 5, 2, and 1, and use the general meta-strategy to figure out
 which one does best.
 
 In fact, Iocaine even varies the horizon of its meta-strategy analyzer!
 Strategies are compared over the last 1000, 100, 10, 5, 2, and 1 moves, and
 a meta-meta-strategy decides which meta-strategy to use (based on which
 picker performed best over the total history of the game). This was designed
 to defeat contestants which switch strategy, and to outfox variants of the
 simpler, older version of Iocaine Powder.
 
 Summary
 
 One must remember, when participating in a contest of this type, that we are
 not attempting to model natural phenomena or predict user actions; instead,
 these programs are competing against hostile opponents who are trying very
 hard not to be predictable. Iocaine Powder doesn't use advanced statistical
 techniques or Markov models (though it could perhaps be improved if it did),
 but it is very devious.
 
 It is, however, by no means the last word. Iocaine may have defeated all
 comers in the first tournament, but I have no doubt that my opponents will
 rise to the challenge in upcoming events.
   ------------------------------------------------------------------------
   Dan Egnor
*/

#define will_beat(play) ("\001\002\000"[play])
#define will_lose_to(play) ("\002\000\001"[play])

/* ------------------------------------------------------------------------- */

static const int my_hist = 0,opp_hist = 1,both_hist = 2;

static int match_single(int i,int num,int *history) {
    int *highptr = history + num;
    int *lowptr = history + i;
    while (lowptr > history && *lowptr == *highptr) --lowptr, --highptr;
    return history + num - highptr;
}

static int match_both(int i,int num) {
    int j;
    for (j = 0; j < i && opp_history[num-j] == opp_history[i-j]
              && my_history[num-j]  == my_history[i-j]; ++j) ;
    return j;
}

static void do_history(int age,int best[3]) {
    const int num = my_history[0];
    int best_length[3],i,j,w;

    for (w = 0; w < 3; ++w) best[w] = best_length[w] = 0; 
    for (i = num - 1; i > num - age && i > best_length[my_hist]; --i) {
        j = match_single(i,num,my_history);
        if (j > best_length[my_hist]) {
            best_length[my_hist] = j;
            best[my_hist] = i;
            if (j > num / 2) break;
        }
    }

    for (i = num - 1; i > num - age && i > best_length[opp_hist]; --i) {
        j = match_single(i,num,opp_history);
        if (j > best_length[opp_hist]) {
            best_length[opp_hist] = j;
            best[opp_hist] = i;
            if (j > num / 2) break;
        }
    }

    for (i = num - 1; i > num - age && i > best_length[both_hist]; --i) {
        j = match_both(i,num);
        if (j > best_length[both_hist]) {
            best_length[both_hist] = j;
            best[both_hist] = i;
            if (j > num / 2) break;
        }
    }
}

/* ------------------------------------------------------------------------- */

struct stats {
    int sum[1 + trials][3];
    int age;
};

static void reset_stats(struct stats *st) {
    int i;
    st->age = 0;
    for (i = 0; i < 3; ++i) st->sum[st->age][i] = 0;
}

static void add_stats(struct stats *st,int i,int delta) {
    st->sum[st->age][i] += delta;
}

static void next_stats(struct stats *st) {
    if (st->age < trials) {
        int i;
        ++(st->age);
        for (i = 0; i < 3; ++i) 
            st->sum[st->age][i] = st->sum[st->age - 1][i];
    }
}

static int max_stats(const struct stats *st,int age,int *which,int *score) {
    int i;
    *which = -1;
    for (i = 0; i < 3; ++i) {
        int diff;
        if (age > st->age) 
            diff = st->sum[st->age][i];
        else
            diff = st->sum[st->age][i] - st->sum[st->age - age][i];
        if (diff > *score) {
            *score = diff;
            *which = i;
        }
    }

    return -1 != *which;
}

/* ------------------------------------------------------------------------- */

struct predict {
    struct stats st;
    int last;
};

static void reset_predict(struct predict *pred) {
    reset_stats(&pred->st);
    pred->last = -1;
}

/* last: opponent's last move (-1 if none)
 | guess: algorithm's prediction of opponent's next move */
static void do_predict(struct predict *pred,int last,int guess) {
    if (-1 != last) {
        const int diff = (3 + last - pred->last) % 3;
        add_stats(&pred->st,will_beat(diff),1);
        add_stats(&pred->st,will_lose_to(diff),-1);
        next_stats(&pred->st);
    }

    pred->last = guess;
}

static void scan_predict(struct predict *pred,int age,int *move,int *score) {
    int i;
    if (max_stats(&pred->st,age,&i,score)) *move = ((pred->last + i) % 3);
}

/* ------------------------------------------------------------------------- */

static const int ages[] = { 1000, 100, 10, 5, 2, 1 };
#define num_ages (sizeof(ages) / sizeof(ages[0]))

struct iocaine {
    struct predict pr_history[num_ages][3][2],pr_freq[num_ages][2];
    struct predict pr_fixed,pr_random,pr_meta[num_ages];
    struct stats stats[2];
};

static int iocaine(struct iocaine *i) {
    const int num = my_history[0];
    const int last = (num > 0) ? opp_history[num] : -1;
    const int guess = biased_roshambo(1.0/3.0,1.0/3.0);
    int w,a,p;

    if (0 == num) {
        for (a = 0; a < num_ages; ++a) {
            reset_predict(&i->pr_meta[a]);
            for (p = 0; p < 2; ++p) {
                for (w = 0; w < 3; ++w)
                    reset_predict(&i->pr_history[a][w][p]);
                reset_predict(&i->pr_freq[a][p]);
            }
        }
        for (p = 0; p < 2; ++p) reset_stats(&i->stats[p]);
        reset_predict(&i->pr_random);
        reset_predict(&i->pr_fixed);
    } else {
        add_stats(&i->stats[0],my_history[num],1);
        add_stats(&i->stats[1],opp_history[num],1);
    }

    for (a = 0; a < num_ages; ++a) {
        int best[3];
        do_history(ages[a],best);
        for (w = 0; w < 3; ++w) {
            const int b = best[w];
            if (0 == b) {
                do_predict(&i->pr_history[a][w][0],last,guess);
                do_predict(&i->pr_history[a][w][1],last,guess);
                continue;
            }
            do_predict(&i->pr_history[a][w][0],last,my_history[b+1]);
            do_predict(&i->pr_history[a][w][1],last,opp_history[b+1]);
        }

        for (p = 0; p < 2; ++p) {
            int best = -1,freq;
            if (max_stats(&i->stats[p],ages[a],&freq,&best))
                do_predict(&i->pr_freq[a][p],last,freq);
            else
                do_predict(&i->pr_freq[a][p],last,guess);
        }
    }

    do_predict(&i->pr_random,last,guess);
    do_predict(&i->pr_fixed,last,0);

    for (a = 0; a < num_ages; ++a) {
        int aa,score = -1,move = -1;
        for (aa = 0; aa < num_ages; ++aa) {
            for (p = 0; p < 2; ++p) {
                for (w = 0; w < 3; ++w)
                    scan_predict(&i->pr_history[aa][w][p],
                             ages[a],&move,&score);
                scan_predict(&i->pr_freq[aa][p],ages[a],&move,&score);
            }
        }

        scan_predict(&i->pr_random,ages[a],&move,&score);
        scan_predict(&i->pr_fixed,ages[a],&move,&score);
        do_predict(&i->pr_meta[a],last,move);
    }

    {
        int score = -1,move = -1;
        for (a = 0; a < num_ages; ++a)
            scan_predict(&i->pr_meta[a],trials,&move,&score);
        return move;
    }
}

/* ------------------------------------------------------------------------- */

int iocainebot(void)
{
    static struct iocaine p;
    return iocaine(&p);
}
/**********************************************************************/


/*  Entrant:  Phasenbott (2)   Jakob Mandelson (USA)
 
 Phasenbott uses a similar strategy to Dan Egnor's "Iocaine Powder", 
 indeed it is derived from an early version of Dan's work.
 
 The early Iocaine Powder ("Old IP") took a single strategy as input, and
 "conjugated" it into six strategies:
   1. Play the strategy.
   2. Assume opponent thinks you'll play the strategy, and beat that.
   3. Assume opponent thinks you'll do (2), and beat that.
   4. Assume opponent plays strategy, and beat that.
   5. Assume opponent thinks you'll do (4), and beat that.
   6. Assume opponent thinks you'll do (5), and beat that.
 
 Because of the circular nature of the Rock beats Scissors beats Paper 
 beats Rock, if you assume the opponent thinks you'll do (3) then you'll
 play (1), and if you assume the opponent thinks you'll do (6) then you'll
 play (4), so these six "strategies" subsume a whole slew of second-guessing.
 (All assuming the initial strategy, though.)  Then it counts which one would
 have done best historically if played, and chooses that strategy to play.
 Old IP used a history match as its base strategy.
 
 I generalised this concept into a function which took in an array of
 "bots" (each of which returns what it would play if it were you, and if
 it were your opponent), did the six-way conjugation on each, and chose the 
 best strategy of those to play.  Note that this function is itself a "bot", 
 and can be fed into itself.  If you consider the operator I to take 
 strategies and choose the best among their conjugates, then Old IP can be
 represented by I(History).  Phasenbott uses a alternate history mechanism
 which performed better, in addition to Dan's original history mechanism and
 Old IP and Random (as a fallback) for its set of base strategies.
 Phasenbott=I(History, AltHistory, Old IP, Random)
 
 "New" IP (Dan's winning program) effectly subsumes Phasenbott, so it's
 no surprise that Phasenbott lost to it.  It uses the new history mechanism
 in addition to the original one, like Phasenbott, and also incorporates
 frequency analysis.  In addition, at the very end after it's applied the 
 various strategies, it applies the I operator to the result!  This means
 it's effectively checking to see how well it would do by playing to beat/lose
 to itself, and playing that if it is better.  I've checked the effects of
 this "meta-ing", and after the first couple steps it's not worthwhile:
 If one of the base strategies doesn't match the opponent's play, then 
 Iocaine's strategy becomes so subtle as to be effectively random.  If one
 of the base strategies does associate with the opponent, then the meta-ing
 does no good.
 
 Iocaine Powder also uses a more accurate metric for comparing the strategies.
 Where Phasenbott plays the strategy that results in the most wins, Iocaine
 Powder takes draws (or losses, depending on your POV) into account, and plays
 the highest scorer.  Phasenbott's metric would be more appropriate in a 
 non-zero sum Rock-Paper-Scissors game where one simply tallied points for
 wins.  This game is more interesting from the theoretical standpoint, as
 there is now incentive for cooperation and no longer a single optimal 
 strategy.  Random scores an expected 1/3, but cooperating players could
 do better by alternating wins, for 1/2.  A player wanting to do better than 
 1/2 would try to exploit the other player, but not enough that the other
 player detects that it's worthwhile to switch into Random mode.  The weak
 player scoring say 2/5 could know that it's being exploited by the stronger,
 but still go along with it as if it refused (by going Random) its score would
 drop to 1/3.  This in my mind makes for a much more interesting 
 Rock-Paper-Scissors game to study than "Roshambo".  Maybe the next 
 Rock-Paper-Scissors programming contest will feature such a non-zero sum
 game.  [Hint, hint. :) ]
 */

/*  Phasenbott  --   Jakob Mandelson.
 *    Roshambo competition program
 *    Looks at a series of strategies, and compares how they did historically.
 *    Then plays one that would have played best.
 *    Strategies used: Historical prediction based on sequence of both parties,
 *      and of one party, and itself using only both-party history prediction.
 *    Based on early Iocaine Powder bot of Dan Egnor of playing strategy
 *      that would have done best historically.  Used with permission,
 *      and some ideas crossed back into Dan's Iocaine.
 *    May the best program (more likely Dan's than mine :) win!
 */

#define pwill_beat(x) ("\001\002\000"[x])

typedef struct {
   long (*fcn)(void *state);
   void *state;
} jlmbot;

typedef struct {
   int both, my, opp, num;
} jlmhistret;

static void jlm_history(jlmhistret *s) {
    int besta,bestb,bestc,i,j,num;
    /* a is both history, b is my history, c is opponent history. */

    if (s->num == my_history[0]) return;
    s->num = num = my_history[0];
    s->both = s->my = s->opp = besta = bestb = bestc = 0;
    for (i = num - 1; i > besta; --i) {
        for (j = 0; j < i 
                && opp_history[num - j] == opp_history[i - j]
                && my_history[num - j] == my_history[i - j]; ++j) { } 
        if (j > besta) { besta = j; s->both = i; }
        if (j > bestb) { bestb = j; s->my = i; }
        if (j > bestc) { bestc = j; s->opp = i; }
        if (opp_history[num-j] != opp_history[i - j]) {
            for ( ; j < i && my_history[num-j] == my_history[i-j]; ++j) { }
            if (j > bestb) { bestb = j; s->my = i; }
        }
        else /* j >= i || my_history[num-j] != my_history[i - j] */ {
            for ( ; j < i && opp_history[num-j] == opp_history[i-j]; ++j) { }
            if (j > bestc) { bestc = j; s->opp = i; }
        }
    }
}

static long jlmhist1(jlmhistret *s) {
        jlm_history(s);
        if (0 == s->opp) return biased_roshambo(1.0/3.0,1.0/3.0);
        return pwill_beat(opp_history[s->opp + 1]) | 
                (pwill_beat(my_history[s->my + 1]) << 16) ;
}

static long jlmhist0(jlmhistret *s) {
        jlm_history(s);
        if (0 == s->both) return biased_roshambo(1.0/3.0,1.0/3.0);
        return pwill_beat(opp_history[s->both + 1]) | 
                (pwill_beat(my_history[s->both + 1]) << 16) ;
}

static long jlmrand(void *throwaway) {  
    /* Fallback to keep from losing too badly.  */
        return biased_roshambo(1.0/3.0, 1.0/3.0) |
                (biased_roshambo(1.0/3.0, 1.0/3.0) << 16);
}

typedef struct {
  int n;
  int *my_last, *opp_last;
  int (*my_stats)[3], (*opp_stats)[3];
  int (*my_ostats)[3], (*opp_ostats)[3];
  int *opp_guess, *my_guess;
  jlmbot *to_beat;
} jocaine_state;

static long apply_jocaine(jocaine_state *);

int phasenbott()
{
   typedef long (*fcn)(void *state);
   typedef int arr4[4];
   static jlmhistret h;
   static arr4 my_last, opp_last, opp_guess, my_guess;
   static int my_stats[4][3], opp_stats[4][3], my_ostats[4][3], 
                opp_ostats[4][3];
   static int sy_last, spp_last, spp_guess, sy_guess;
   static int sy_stats[3], spp_stats[3], sy_ostats[3], spp_ostats[3];
   static jlmbot hb = { (fcn)jlmhist0,  &h};
   static jocaine_state t = { 1, &sy_last, &spp_last,
                              &sy_stats, &spp_stats, &sy_ostats, &spp_ostats,
                              &spp_guess, &sy_guess, &hb };
   static jlmbot ba[4] = {{(fcn)jlmhist1, &h}, {(fcn)jlmhist0, &h}, 
                          {(fcn)jlmrand, 0}, {(fcn)apply_jocaine, &t}};
   static jocaine_state s = { 4, my_last, opp_last,
                              my_stats, opp_stats, my_ostats, opp_ostats,
                              opp_guess, my_guess, ba};
   return apply_jocaine(&s) & 0xFFFF;
}

static long apply_jocaine(jocaine_state *s) {
        const int num = my_history[0];
        long b;
        int i,my_most,opp_most, h;
        int my_omost, opp_omost;
        int hy_omost, hpp_omost;
        int hy_most, hpp_most;

        if (0 == num) {
            for (h = 0; h < s->n; h++)
            {   for (i = 0; i < 3; ++i) 
                        s->my_stats[h][i] = s->opp_stats[h][i] = 
                        s->my_ostats[h][i] = s->opp_ostats[h][i] = 0;
                b = s->to_beat[h].fcn(s->to_beat[h].state);
                s->my_last[h] =  b & 0xFFFF;
                s->opp_last[h] =  b >> 16; 
            }
            return random()%3;
        }

     for (h = 0; h < s->n; h++)
     {
        b = s->to_beat[h].fcn(s->to_beat[h].state); 
        s->my_guess[h] = b & 0xFFFF;
        s->opp_guess[h] = b >> 16;

        s->my_stats[h][(3 + opp_history[num] - s->my_last[h]) % 3]++;
        s->opp_stats[h][(3 + opp_history[num] - s->opp_last[h]) % 3]++;
        s->my_ostats[h][(3 + my_history[num] - s->opp_last[h]) % 3]++;
        s->opp_ostats[h][(3 + my_history[num] - s->my_last[h]) % 3]++;

        s->my_last[h] = s->my_guess[h];
        s->opp_last[h] = s->opp_guess[h];
    }

        my_most = opp_most = my_omost = opp_omost = 0;
        hy_most = hpp_most = hy_omost = hpp_omost = 0;
        for (h = 0; h < s->n; ++h) 
            for (i = 0; i < 3; ++i) {
                if (s->my_stats[h][i] > s->my_stats[hy_most][my_most]) 
                        { my_most = i; hy_most = h; }
                if (s->opp_stats[h][i] > s->opp_stats[hpp_most][opp_most]) 
                        { opp_most = i; hpp_most = h; }
                if (s->my_ostats[h][i] > s->my_ostats[hy_omost][my_omost]) 
                        { my_omost = i; hy_omost = h; }
                if (s->opp_ostats[h][i] > s->opp_ostats[hpp_omost][opp_omost]) 
                        { opp_omost = i; hpp_omost = h; }
            }

        if (s->opp_stats[hpp_most][opp_most] >= s->my_stats[hy_most][my_most])
                b = pwill_beat((s->opp_guess[hpp_most] + opp_most) % 3);
        else
                b = pwill_beat((s->my_guess[hy_most] + my_most) % 3);

        if (s->opp_ostats[hpp_omost][opp_omost] 
                        >= s->my_ostats[hy_omost][my_omost])
                b |= pwill_beat((s->my_guess[hpp_omost] + opp_omost) % 3) << 16;
        else
                b |= pwill_beat((s->opp_guess[hy_omost] + my_omost) % 3) << 16;

        return b;
}
/**********************************************************************/


/*  Entrant:  MegaHAL (3)   Jason Hutchens (Aus)

 MegaHAL     (from: http://ciips.ee.uwa.edu.au/~hutch/puzzles/roshambo/)
 
 MegaHAL, named in honour of a conversation simulator of mine, was my entry
 into the First International RoShamBo Programming Competition, which was
 conducted by Darse Billings. MegaHAL came third in the competition, behind
 the excellent Iocaine Powder of Dan Egnor, and Phasenbott by Jakob
 Mandelson. This web page is a brief attempt to explain how the MegaHAL
 algorithm works.
 
 Source Code
 
 Please feel free to download the source code to the MegaHAL algorithm. To
 compile it with Darse's tournament program (available from the competition
 home page), I recommend that you modify the tournament program by adding an
 external declaration to the halbot() function, and then linking the code as
 follows:
 
 gcc -o roshambo roshambo.c megahal.c
 
 I have also written a simple program which allows a human being to play
 against a RoShamBo algorithm. You may compile that as follows:
 
 gcc -o shell shell.c megahallc -lcurses
 
    * megahal.c (18Kb)
    * shell.c (15Kb)
 
 Prediction
 
 My opinion, as I have stated on the comp.ai.games newsgroup often enough,
 is that Darse's competition provides an ideal test-bed for predictive
 algorithms, or predictors. I have worked with predictors for the last five
 years, applying them to various syntactic pattern recognition problems,
 speech recognition, text generation and data compression.
 
 A predictor is an algorithm which is able to predict the next symbol in a
 sequence of symbols as a probability distribution over the alphabet of
 symbols. The only information available to the predictor is the history of
 symbols seen so far. In order to turn a predictor into a RoShamBo algorithm,
 we need to decide what the history of symbols should be, and how to turn a
 prediction into a RoShamBo move.
 
 Determining the history
      Because we are trying to predict our opponent's next move, and because
      our opponent may be using our previous moves to decide what they're
      going to do, it seems reasonable to make the symbol sequence an
      interlacing of both our histories: x1,y1,x2,y2,..., xn-1,yn-1, where x
      represents our opponent's move, y represents our move, and our job is
      to predict the value of xn in order to determine what yn should be.
 Choosing our move
      Once we have a prediction for yn in the form of a probability
      distribution over all possible moves, we need to decide what our move
      is going to be. We do this by choosing the move which maximises the
      expected value of our score. For example, imagine that the prediction
      gives P(rock)=0.45, P(paper)=0.15, P(scissors)=0.40. The maximum
      likelihood move (paper) gives an expected score of 1*0.45-1*0.40=0.05,
      while the defensive move of rock gives an expected score of
      1*0.40-1*0.15=0.25, and is therefore chosen.
 
 With these two modifications, any predictor may play RoShamBo!
 
 The MegaHAL Predictor
 
 MegaHAL is a very simple "infinite-order" Markov model. It stores frequency
 information about the moves the opponent has made in the past for all
 possible contexts (from a context of no symbols at all right up to a context
 of the entire history). In practise, the context is limited to forty-two
 symbols so that the algorithm satisfies the time constraint of playing one
 game every millisecond on average.
 
 MegaHAL stores this information in a ternary trie. Each context is
 represented as a node in this trie. Every time MegaHAL is asked to make a
 move, many of these nodes may activate, and each of them is capable of
 providing us with a prediction about what's coming next. We need to select
 one of them. We do this by storing in each node the average score that that
 node would have if it had been used exclusively in the past. We select the
 node which has the highest average score. If more than one node qualifies,
 we choose the one which takes the longest context into account.
 
 In some situations, no nodes will be selected. In this situation, we make a
 move at random.
 
 MegaHAL also gathers statistics over a sliding window, which means that it
 "forgets" about events which occurred a long time ago. This process allows
 MegaHAL to adapt more rapidly to changes in its opponents strategy. In the
 competition version, a sliding window of four hundred symbols was used (a
 match consists of two thousand symbols).
 
 Conclusion
 
 I hope that brief explanation of the MegaHAL strategy has been enlightening.
 I apologise for any omissions or poor English, and blame that on the fact
 that it was written at 12:45pm on a Saturday night, following a night out
 with friends!
*/

/*============================================================================*/
/*
 *  Copyright (C) 1999 Jason Hutchens
 *
 *  This program is free software; you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by the Free
 *  Software Foundation; either version 2 of the license or (at your option)
 *  any later version.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 *  or FITNESS FOR A PARTICULAR PURPOSE.  See the Gnu Public License for more
 *  details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  675 Mass Ave, Cambridge, MA 02139, USA.
 */
/*============================================================================*/
/*
 *      NB:      File displays best with tabstops set to three spaces.
 *
 *      Name:      MegaHAL (in honour of http://ciips.ee.uwa.edu.au/~hutch/hal/)
 *
 *      Author:   Jason Hutchens (hutch@amristar.com.au)
 *
 *      Purpose:   Play the game of Rock-Paper-Scissors.  Statistics about the
 *               game so far are recorded in a ternary trie, represnting an
 *               infinite-order Markov model.  The context which has performed
 *               best in the past is used to make the prediction, and we
 *               gradually fall-back through contexts which performed less well
 *               when the contexts haven't yet been observed.  One of the
 *               contexts is always guaranteed to make a move at random, so
 *               we never encounter a situation where we can't make a move.
 *               Statistics are gathered over a sliding window, allowing
 *               adaption if the opponent's strategies change.
 *
 *      $Id: megahal.c,v 1.8 1999/09/16 03:18:27 hutch Exp hutch $
 */
/*============================================================================*/

/*============================================================================*/

int halbot(void);
static int halbot_compare(const void *, const void *);

/*============================================================================*/
/*
 *      Function:   halbot
 *
 *      Arguments:   void
 *
 *      Returns:      An integer between 0 and 2, representing the move that the
 *                  predictor makes in the game of Rock-Paper-Scissors.
 *
 *      Overview:   The program collects statistics about the game using an
 *                  infinite context Markov model, which is stored in a ternary
 *                  trie.  The procedure is to update the statistics of the
 *                  model with the latest moves, and remove the statistics of
 *                  moves outside a sliding window of defined length.  We build
 *                  an array of contexts which make valid predictions, including
 *                  the special context which always predicts at random, and we
 *                  sort this according to how well the contexts have performed
 *                  in the recent past (again with the sliding window).  The
 *                  best context is then used to make the prediction, and our
 *                  move is selected in order to maximise the expected value of
 *                  the score.  The bot monitors how much time it's been
 *                  spending, and emits a message when this time exceeds an
 *                  average of one millisecond per move (i.e. one second per
 *                  one thousand moves).
 *
 *      Comment:      Even though it's really messy, everything is done in this
 *                  one function to allow it to be added to the competition
 *                  source code easily.
 */
int halbot(void)
{
   /*
    *      Set this to a non-zero value to emit an warning message if the
    *      algorithm averages more than one millisecond per move.
    */
   #define   ERROR      0
   /*
    *      These defines are the three heuristic parameters that can be modified
    *      to alter performance.  BELIEVE gives the number of times a context
    *      must be observed before being used for prediction, HISTORY gives the
    *      maximum context size to observe (we're limited by time, not memory),
    *      and WINDOW gives the size of the sliding window, 0 being infinite.
    *
    *      - BELIEVE>=1
    *      - HISTORY>=1
    *      - WINDOW>=HISTORY or 0 for infinite
    */
   #define   BELIEVE   1
   #define   HISTORY   21
   #define   WINDOW   200
   /*
    *      This define just makes the code neater (huh, as if).
    */
   #define   COUNT      trie[context[i].node].move
   #define   SCOUNT   trie[sorted[i].node].move
   /*
    *      These macros returns the maximum/minimum values of two expressions.
    */
   #define   MAX(a,b)   (((a)>(b))?(a):(b))
   #define   MIN(a,b)   (((a)<(b))?(a):(b))
   /*
    *      Each node of the trie contains frequency information about the moves
    *      made at the context represented by the node, and where the sequent
    *      nodes are in the array.
    */
   typedef struct S_NODE {
      short int total;
      short int move[3];
      int next[3];
   } NODE;
   /*
    *      The context array contains information about contexts of various
    *      lengths, and this is used to select a context to make the prediction.
    */
   typedef struct S_CONTEXT {
      int worst;
      int best;
      int seen;
      int size;
      int node;
   } CONTEXT;
   /*
    *      This is the only external information we have about our opponent;
    *      it's a history of the game so far.
    */
   extern int my_history[];
   extern int opp_history[];
   /*
    *      We declare all variables as statics because we want most of them to
    *      be persistent.
    */
   static int move=-1;
   static int last_move=-1;
   static int random_move=-1;
   static NODE *trie=NULL;
   static int trie_size=0;
   static int context_size=0;
   static CONTEXT *context=NULL;
   static CONTEXT *sorted=NULL;
   static int **memory=NULL;
   static int remember=0;
   static struct timeval start;
   static struct timeval end;
   static long think;
   static int node;
   static int expected[3];
   /*
    *      But you canny have static register variables!
    */
   register int i,j;
   /*
    *      Start the timer.
    */
   (void)gettimeofday(&start,NULL);
   /*
    *      If this is the beginning of the game, set some things up.
    */
   if(my_history[0]==0) {
      if(trie==NULL) {
         /*
          *      If this is the first game we've played, initialise the memory.
          *      On some Unices, realloc doesn't work with NULL arguments, so
          *      we're just making sure they're non-NULL.
          *
          *      NB: We must allocate two elements for the context!
          */
         context=(CONTEXT *)malloc(sizeof(CONTEXT)*(HISTORY+2));
         assert(context);
         sorted=(CONTEXT *)malloc(sizeof(CONTEXT)*(HISTORY+2));
         assert(sorted);
         if(WINDOW>0) {
            memory=(int **)malloc(sizeof(int *)*WINDOW);
            assert(memory);
            for(i=0; i<WINDOW; ++i) {
               memory[i]=(int *)malloc(sizeof(int)*(HISTORY+2));
               assert(memory[i]);
            }
         }
         trie=(NODE *)malloc(sizeof(NODE));
         assert(trie);
      }
      /*
       *      Clear the trie, by setting its size to unity, and clearing the
       *      statistics of the root node.
       */
      trie_size=1;
      trie[0]=(NODE){0,{0,0,0},{-1,-1,-1}};
      /*
       *      Clear the memory matrix.
       */
      for(i=0; i<WINDOW; ++i)
         for(j=0; j<HISTORY+2; ++j)
            memory[i][j]=-1;
      /*
       *      Clear the context array.
       */
      for(i=0; i<HISTORY+2; ++i) context[i]=(CONTEXT){0,0,0,0,0};
      context[0]=(CONTEXT){0,0,0,-1,-1};
      context[1]=(CONTEXT){0,0,0,0,0};
      /*
       *      Clear the variable we use to keep track of how long MegaHAL
       *      spends thinking.
       */
      think=0;
   }
   /*
    *      If we've already started playing, evaluate how well we went on our
    *      last turn, and update our list which decides which contexts give the
    *      best predictions.
    */
   if(my_history[0]>0) {
      /*
       *      We begin by forgetting which contexts performed well in the
       *      distant past.
        */
      if(WINDOW>0) for(i=1; i<context_size; ++i) {
         if(WINDOW-i>0) {
            if(memory[(remember+i-1)%WINDOW][i]>=0) {
               if(memory[(remember+i-1)%WINDOW][i]==
                  ((opp_history[my_history[0]-WINDOW+i-1]+1)%3))
                     context[i].best-=1;
               if(memory[(remember+i-1)%WINDOW][i]==
                  ((opp_history[my_history[0]-WINDOW+i-1]+2)%3))
                     context[i].worst-=1;
               context[i].seen-=1;
            }
         }
      }
      /*
       *      Clear our dimmest memory.
       */
      if(WINDOW>0) for(i=0; i<context_size; ++i)
         memory[remember][i]=-1;
      /*
       *      We then remember the contexts which performed the best most
       *      recently.
       */
      for(i=0; i<context_size; ++i) {
         if(context[i].node>=trie_size) continue;
         if(context[i].node==-1) continue;
         if(trie[context[i].node].total>=BELIEVE) {
            for(j=0; j<3; ++j)
               expected[j]=COUNT[(j+2)%3]-COUNT[(j+1)%3];
            last_move=0;
            for(j=1; j<3; ++j)
               if(expected[j]>expected[last_move])
                  last_move=j;
            if(last_move==(opp_history[my_history[0]]+1)%3)
               context[i].best+=1;
            if(last_move==(opp_history[my_history[0]]+2)%3)
               context[i].worst+=1;
            context[i].seen+=1;
            if(WINDOW>0) memory[remember][i]=last_move;
         }
      }
      if(WINDOW>0) remember=(remember+1)%WINDOW;
   }
   /*
    *      Clear the context to the node which always predicts at random, and
    *      the root node.
    */
   context_size=2;
   /*
    *      We begin by forgetting the statistics we've previously gathered
    *      about the symbol which is now leaving the sliding window.
    */
   if((WINDOW>0)&&(my_history[0]-WINDOW>0))
      for(i=my_history[0]-WINDOW;
         i<MIN(my_history[0]-WINDOW+HISTORY,my_history[0]); ++i) {
      /*
       *      Find the node which corresponds to the context.
       */
      node=0;
      for(j=MAX(my_history[0]-WINDOW,1); j<i; ++j) {
         node=trie[node].next[opp_history[j]];
         node=trie[node].next[my_history[j]];
      }
      if((node<0)||(node>=trie_size))fprintf(stderr, "OUCH\n");
      /*
       *      Update the statistics of this node with the opponents move.
       */
      trie[node].total-=1;
      trie[node].move[opp_history[i]]-=1;
   }
   /*
    *      Build up a context array pointing at all the nodes in the trie
    *      which predict what the opponent is going to do for the current
    *      history.  While doing this, update the statistics of the trie with
    *      the last move made by ourselves and our opponent.
    */
#if(WINDOW>0)
   for(i=my_history[0]; i>MAX(my_history[0]-MIN(WINDOW,HISTORY),0); --i) {
#else
   for(i=my_history[0]; i>MAX(my_history[0]-HISTORY,0); --i) {
#endif
      /*
       *      Find the node which corresponds to the context.
       */
      node=0;
      for(j=i; j<my_history[0]; ++j) {
         node=trie[node].next[opp_history[j]];
         node=trie[node].next[my_history[j]];
      }
      if((node<0)||(node>=trie_size))fprintf(stderr, "OUCH\n");
      /*
       *      Update the statistics of this node with the opponents move.
       */
      trie[node].total+=1;
      trie[node].move[opp_history[my_history[0]]]+=1;
      /*
       *      Move to this node, making sure that we've allocated it first.
       */
      if(trie[node].next[opp_history[my_history[0]]]==-1) {
         trie[node].next[opp_history[my_history[0]]]=trie_size;
         trie_size+=1;
         trie=(NODE *)realloc(trie,sizeof(NODE)*trie_size);
         assert(trie);
         trie[trie_size-1]=(NODE){0,{0,0,0},{-1,-1,-1}};
      }
      node=trie[node].next[opp_history[my_history[0]]];
      if((node<0)||(node>=trie_size))fprintf(stderr, "OUCH\n");
      /*
       *      Move to this node, making sure that we've allocated it first.
       */
      if(trie[node].next[my_history[my_history[0]]]==-1) {
         trie[node].next[my_history[my_history[0]]]=trie_size;
         trie_size+=1;
         trie=(NODE *)realloc(trie,sizeof(NODE)*trie_size);
         assert(trie);
         trie[trie_size-1]=(NODE){0,{0,0,0},{-1,-1,-1}};
      }
      node=trie[node].next[my_history[my_history[0]]];
      if((node<0)||(node>=trie_size))fprintf(stderr, "OUCH\n");
      /*
       *      Add this node to the context array.
       */
      context_size+=1;
      context[context_size-1].node=node;
      context[context_size-1].size=context_size-2;
   }
   /*
    *      Sort the context array, based upon what contexts have proved
    *      successful in the past.  We sort the context array by looking
    *      at the context lengths which most often give the best predictions.
    *      If two contexts give the same amount of best predictions, choose
    *      the longest one.  If two contexts have consistently failed in the
    *      past, choose the shortest one.
    */
   for(i=0; i<context_size; ++i)
      sorted[i]=context[i];
   qsort(sorted,context_size,sizeof(CONTEXT),halbot_compare);
   /*
    *      Starting at the most likely context, gradually fall-back until we
    *      find a context which has been observed at least BELIEVE times.  Use
    *      this context to predict a probability distribution over the opponents
    *      possible moves.  Select the move which maximises the expected score.
    */
   move=-1;
   for(i=0; i<context_size; ++i) {
      if(sorted[i].node>=trie_size) continue;
      if(sorted[i].node==-1) break;
      if(trie[sorted[i].node].total>=BELIEVE) {
         for(j=0; j<3; ++j)
            expected[j]=SCOUNT[(j+2)%3]-SCOUNT[(j+1)%3];
         move=0;
         for(j=1; j<3; ++j)
            if(expected[j]>expected[move])
               move=j;
         break;
      }
   }
   /*
    *      If no prediction was possible, make a random move.
    */
   random_move=random()%3;
   if(move==-1) move=random_move;
   /*
    *      Update the timer, and warn if we've exceeded one second per one
    *      thousand turns.
    */
   (void)gettimeofday(&end,NULL);
   if(think>=0)
      think+=1000000*(end.tv_sec-start.tv_sec)+(end.tv_usec-start.tv_usec);
   if((ERROR!=0)&&((think/(my_history[0]+1)>=1000)&&(my_history[0]>100))) {
      think=-1;
      fprintf(stdout, "\n\n*** MegaHAL-Infinite is too slow! ***\n\n");
   }
   /*
    *      Return our move.
    */
   return(move);

}   /* end "halbot" */

/*----------------------------------------------------------------------------*/
/*
 *      Function:   halbot_compare
 *
 *      Arguments:   const void *value1, const void *value2
 *                  Two pointers into the sort array.  Our job is to decide
 *                  whether value1 is less than, equal to or greater than
 *                  value2.
 *
 *      Returns:      An integer which is positive if value1<value2, negative if
 *                  value1>value2, and zero if they're equal.  Various heuristics
 *                  are used to test for this inequality.
 *
 *      Overview:   This comparison function is required by qsort().
 */
static int halbot_compare(const void *value1, const void *value2)
{
   /*
    *      This is a duplicate of the typedef in halbot(), put here to avoid
    *      having to make it external to the functions.
    */
   typedef struct S_CONTEXT {
      int worst;
      int best;
      int seen;
      int size;
      int node;
   } CONTEXT;
   /*
    *      Some local variables.
    */
   CONTEXT *context1;
   CONTEXT *context2;
   float prob1=0.0;
   float prob2=0.0;
   /*
    *      This looks complicated, but it's not.  Basically, given two nodes
    *      in the trie, these heuristics decide which node should be used to
    *      make a prediction first.  The rules are:
    *      - Choose the one which has performed the best in the past.
    *      - If they're both being tried for the first time, choose the shortest.
    *      - If they've both performed equally well, choose the longest.
    */
   context1=(CONTEXT *)value1;
   context2=(CONTEXT *)value2;
   if(context1->seen>0)
      prob1=(float)(context1->best-context1->worst)/(float)(context1->seen);
   if(context2->seen>0)
      prob2=(float)(context2->best-context2->worst)/(float)(context2->seen);
   if(prob1<prob2) return(1);
   if(prob1>prob2) return(-1);
   if((context1->seen==0)&&(context2->seen=0)) {
      if(context1->size<context2->size) return(-1);
      if(context1->size>context2->size) return(1);
      return(0);
   }
   if(context1->size<context2->size) return(1);
   if(context1->size>context2->size) return(-1);
   return(0);

}   /* end of "halbot_compare" */

/*============================================================================*/
/*
 *      $Log: megahal.c,v $
 *      Revision 1.7  1999/09/16 03:16:55  hutch
 *      Did some speed improvements, improved the method of remembering past
 *      strategies, and imroved the heuristics for sorting.  Over 1000 tourneys
 *      of 1000 trials, it performed 17.6 times better than the second best bot,
 *      "Beat Last Move", and scored an average of 678 per match.  It also
 *      consistently beats version 1.1, scoring an average of 100 or so per
 *      match.
 *
 *      Revision 1.5  1999/09/13 16:51:57  hutch
 *      The sliding window is working perfectly.  Of course, this strategy
 *      doesn't improve the performance of MegaHAL-Infinite on the standard
 *      algorithms, but it will hopefully improve performance on smarter ones.
 *
 *      Revision 1.4  1999/09/13 14:48:57  hutch
 *      Cleaned up the source a bit, and prepared to implement the sliding
 *      window strategy.
 *
 *      Revision 1.3  1999/09/12 06:29:30  hutch
 *      Consideration of the statistics, and correcting it to give proper
 *      probability estimates, improved Megahal-Infinite beyond MegaHAL.
 *
 *      Revision 1.2  1999/09/12 06:23:02  hutch
 *      Infinite contexts are done, and we now choose the context that has
 *      performed the best in the past.  Doesn't perform as well as MegaHAL,
 *      but I believe it will perform better on craftier algorithms.  Plus
 *      it out-performs MegaHAL on R-P-S 20-20-60.
 *
 *      Revision 1.1  1999/09/12 03:53:08  hutch
 *      This is the first official version.  We are now going to concentrate
 *      on making an infinite-context model, and collecting statistics over
 *      a sliding window, in the hope that this will improve performance
 *      against more sophisticated algorithms.
 *
 *      Revision 0.4  1999/09/11 12:40:11  hutch
 *      Okay, experimentation with parameters has increased it's performance to
 *      about 15 times better than the second best bot, and it's near perfect on
 *      "Beat Last Move", "Beat Frequent Pick", "Rotate RPS" and "Good Ol Rock".
 *      It scores about half on "Always Switchin'", and about a third on "R-P-S
 *      20-20-60".  Interestingly, this is the only bot which it has difficulty
 *      with.  Over 1000 tourneys of 1000 trials, it performed 17.5 times better
 *      than the second best bot, "Beat Last Move", and scored an average of 677
 *      per match.
 *
 *      Revision 0.3  1999/09/11 12:33:54  hutch
 *      Everything is working; the program kicks ass against the standard bots
 *      (performing at least twelve times better than the second best).  I will
 *      fine-tune the algorithm a bit, although it is quite quick, and will play
 *      around with the heuristics before submitting.
 *
 *      Revision 0.2  1999/09/11 11:40:01  hutch
 *      The mechanism for selecting the best move has been finished, and the
 *      model is working for a NULL context.  Now we need to expand it to the
 *      infinite context.
 *
 *      Revision 0.1  1999/09/11 05:58:29  hutch
 *      Initial revision
 */
/*============================================================================*/
/**********************************************************************/


/*  Entrant:  RussRocker4 (4)   Russ Williams (USA)

   > I also welcome more feedback from the participants,
 
 Ok, here's some more feedback & personal info for you.  Feel free to include
 any of it at your site if it seems of interest.
 
 You summed up the basic idea of my AI pretty well in your Part 1 report.  I
 basically made a Markov model of the other player's actions, given the last
 3 moves of both players and basing the probabilities on the entire match
 history.  I then assumed they would simply pick the most likely move.  I
 also used the last 2 moves if the last 3 moves gave a tie for most likely
 guess, and if that still tied, use the last move, and so on.  Experimenting
 showed that using this tie breaking seemed to only be useful early on, so
 after a while ties for most likely opponent choice were broken by choosing
 randomly.
 
 I also intentionally chose to use the large arrays to avoid having to scan
 the entire history array each turn, since I wasn't sure how much of an issue
 execution speed would be.  The cost of that was that there was no simple or
 obvious way to give more emphasis to more recent games, which I would have
 liked to have done.
 
 I'd misunderstood and thought that reverting to random behavior even as a
 "bailout" measure was considered unsporting, else I might have added such a
 feature which would have (as you observed) saved me getting so trounced by
 the rank 1 & 2 programs.  Or did you have some other sort of bailout measure
 in mind?  I could imagine another potentially useful (or at least amusing)
 bailout measure would be "if I'm losing hideously, then start doing the
 opposite of whatever my algorithm says I should do."
 
 I fiddled off & on with my program for about 5 days.  It went through quite
 a few iterations, and I played many long tournaments with variations of
 itself and lots of intentionally weak players to tweak it.
 
 I also found that some versions seemed much stronger at short matches (e.g.
 100 games) and weaker at long matches (e.g. 10000 games), and vice-versa.
 The reasons were not always apparent.
 
 In real life I am a game programmer, which I got into after completing a MS
 in CS at UT Austin.  I worked on 1830 (from Avalon Hill) and Master of Orion
 2 (from Microprose), doing AI for both.  I plan to work on AI for Go one of
 these days.
*/

static int russrock_max(int *a, int n)
{
    int i;
    int best_index = 0;
    int max_so_far = a[0];
    for (i = 1; i < n; ++i) {
        if (max_so_far < a[i]) {
            max_so_far = a[i];
            best_index = i;
        }
    }
    return best_index;
}

int russrocker4()
{
/* by Russ Williams (e-mail: russrocker at hotmail dot com */
    const int n_moves_for_3 = 825;
    const int n_moves_for_2 = 11;
    const int n_moves_for_1 = 6;

    static int moves0[3];
    static int moves1[3][3][3];
    static int moves2[3][3][3][3][3];
    static int moves3[3][3][3][3][3][3][3];

    int max_index, max_value;

    int i, j, n;

    int n_moves = opp_history[0];
    int their_last = -1;

    int temp[3];
    int n_votes[3] = {1, 1, 1};

    if (n_moves == 0) {
        memset(moves0, 0, sizeof moves0);
        memset(moves1, 0, sizeof moves1);
        memset(moves2, 0, sizeof moves2);
        memset(moves3, 0, sizeof moves3);
    } else {
        their_last = opp_history[n_moves];
    }

    switch (n_moves) {
    default:
        ++moves3
            [my_history[n_moves - 3]][opp_history[n_moves - 3]]
            [my_history[n_moves - 2]][opp_history[n_moves - 2]]
            [my_history[n_moves - 1]][opp_history[n_moves - 1]]
            [their_last];
        /*  fall through */
    case 3:
        ++moves2
            [my_history[n_moves - 2]][opp_history[n_moves - 2]]
            [my_history[n_moves - 1]][opp_history[n_moves - 1]]
            [their_last];
        /*  fall through */
    case 2:
        ++moves1
            [my_history[n_moves - 1]][opp_history[n_moves - 1]]
            [their_last];
        /*  fall through */
    case 1:
        ++moves0
            [their_last];
        /*  fall through */
    case 0:
        break;
    }

    do {

        if (3 <= n_moves) {
            for (i = 0; i < 3; ++i) {
                temp[i] = moves3
                    [my_history[n_moves - 2]][opp_history[n_moves - 2]]
                    [my_history[n_moves - 1]][opp_history[n_moves - 1]]
                    [my_history[n_moves]][their_last]
                    [i];
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 10000;
                        ++n;
                    }
                }
                if (n == 1 || n_moves_for_3 <= n_moves) break;
            }

            for (i = 0; i < 3; ++i) {
                temp[i] = 0;
                for (j = 0; j < 3; ++j) {
                    temp[i] += moves3
                        [j][opp_history[n_moves - 2]]
                        [my_history[n_moves - 1]][opp_history[n_moves - 1]]
                        [my_history[n_moves]][their_last]
                        [i]
                        + moves3
                        [my_history[n_moves - 2]][j]
                        [my_history[n_moves - 1]][opp_history[n_moves - 1]]
                        [my_history[n_moves]][their_last]
                        [i];
                }
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 5000;
                        ++n;
                    }
                }
            }
        }

        if (2 <= n_moves) {
            for (i = 0; i < 3; ++i) {
                temp[i] = moves2
                    [my_history[n_moves - 1]][opp_history[n_moves - 1]]
                    [my_history[n_moves]][their_last]
                    [i];
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 1000;
                        ++n;
                    }
                }
                if (n_moves_for_2 <= n_moves) break;
            }

            for (i = 0; i < 3; ++i) {
                temp[i] = 0;
                for (j = 0; j < 3; ++j) {
                    temp[i] += moves2
                        [j][opp_history[n_moves - 1]]
                        [my_history[n_moves]][their_last]
                        [i]
                        + moves2
                        [my_history[n_moves - 1]][j]
                        [my_history[n_moves]][their_last]
                        [i];
                }
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 500;
                        ++n;
                    }
                }
            }
        }

        if (1 <= n_moves) {
            for (i = 0; i < 3; ++i) {
                temp[i] = moves1
                    [my_history[n_moves]][their_last]
                    [i];
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 100;
                        ++n;
                    }
                }
                if (n_moves_for_1 <= n_moves) break;
            }

            for (i = 0; i < 3; ++i) {
                temp[i] = 0;
                for (j = 0; j < 3; ++j) {
                    temp[i] += moves1
                        [j][their_last]
                        [i]
                        + moves1
                        [my_history[n_moves]][j]
                        [i];
                }
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 50;
                        ++n;
                    }
                }
            }
        }

        {
            for (i = 0; i < 3; ++i) {
                temp[i] = moves0
                    [i];
            }
            max_index = russrock_max(temp, 3);
            max_value = temp[max_index];
            if (0 < max_value) {
                n = 0;
                for (i = 0; i < 3; ++i) {
                    if (temp[i] == max_value) {
                        n_votes[i] += 10;
                        ++n;
                    }
                }
            }
        }
    } while (0);

    max_index = russrock_max(n_votes, 3);
    for (i = 0; i < 3; ++i) {
        if (n_votes[i] < n_votes[max_index]) {
            n_votes[i] = 0;
        }
    }

    return (1 + biased_roshambo(n_votes[0]/(double)(n_votes[0] + n_votes[1]
 + n_votes[2]), n_votes[1]/(double)(n_votes[0] + n_votes[1] + n_votes[2]))) % 3;
}
/*  russrocker4  */
/**********************************************************************/


/*  Entrant:  Biopic (5)   Jonathan Schaeffer (Can)  */

/* RoShamBo -- Biopic version that switches between using opponent's and */
/* our history to decide on a strategy.                                  */
/*                                                                       */
/* Jonathan Schaeffer                                                    */
/* September 27, 1999    (debugged version, after the official event)    */

/* Shortcuts, because I am lazy */
#define ME           my_history
#define YOU          opp_history
#define TRIAL        ME [ 0 ]
#define MY_PLAY      ME [ TRIAL ]
#define YOU_PLAY     YOU[ TRIAL ]
#define JRANDOM_MOVE return( random() % 3 );
#define JSINFINITY     (1<<30)

/* Application dependent parameters */
#define WSIZE        25      /* Size of a losing margin? */
#define CSIZE        10      /* Storage inefficient */
#define EV_SCALE     5       /* Used to determine a "small" value */
#define WEIGHTED             /* Bias towards more rather than less context */

extern void bzero();

static int mult[ CSIZE ];

/* Support routines */

#define EV_TTL  ttl = ev[ rock ] + ev[ paper ] + ev[ scissors ];

int BiopicMove( int * wt )
{
    int ev[ 3 ], ttl, i;

    ev[ paper    ] = wt[ rock     ] - wt[ scissors ];
    ev[ rock     ] = wt[ scissors ] - wt[ paper    ];
    ev[ scissors ] = wt[ paper    ] - wt[ rock     ];

    /* Decide */

    /* Make small values 0 */
    EV_TTL
    for( i = 0; i < 3; i++ )
        if( ev[ i ] * EV_SCALE < ttl )
            ev[ i ] = 0;

    /* Make large values big */
    EV_TTL
    for( i = 0; i < 3; i++ )
        if( ev[ i ] * 5 / 3 >= ttl )
            ev[ i ] = 99999;

    /* Decide */
    EV_TTL
    if( ttl <= 0 )
        return( biased_roshambo( (double) 1.0/3, (double) 1.0/3 ) );
    else    return( biased_roshambo( (double) ev[ rock  ] / ttl,
                     (double) ev[ paper ] / ttl ) );
}

void BiopicWeight( int wt[], short int * context[], int * history )
{
    int i, j, ptr[ CSIZE ];

    /* Get indices into context */
    for( j = i = 0; i < CSIZE && TRIAL - i > 0; i++ )
        ptr[ i ] = ( j += history[ TRIAL - i ] * mult[ i ] ) * 3;

    /* Process context */
    wt[ rock ] = wt[ paper ] = wt[ scissors ] = 0;
    for( i = 0; i < CSIZE; i++ )
    {
        if( TRIAL - i <= 0 )
            continue;
        for( j = 0; j < 3; j++ )
            wt[ j ] += context[ i ][ ptr[ i ] + j ]
#ifdef WEIGHTED
                * mult[ i ]
#endif
                ;
    }
}


/* This is it! */

int biopic ()
{
    static int score = -JSINFINITY;
    static int gorandom, move[ 4 ], sc[ 4 ], freq[ 2 ][ 3 ];
    /* Short int limits matches to 32K */
    static short int * myh[ CSIZE ], * oph[ CSIZE ];

    int i, j, ix, wt[3];

    /*
     *
     * Initialize
     *
     */

    /* (1) First time the bot is run */
    if( score == -JSINFINITY )
    {
        for( i = 1, ix = 3; i < CSIZE; i++, ix *= 3 )
            mult[ i ] = ix;
        mult[ 0 ] = 1;
        for( i = 0, ix = 3; i < CSIZE; i++, ix *= 3 )
        {
            myh[ i ] = malloc( ix * sizeof(short int) * 3 );
            oph[ i ] = malloc( ix * sizeof(short int) * 3 );
        }
    }

    /* (2) First hand of a match */
    if( TRIAL == 0 )
    {
        score = gorandom = 0;
        for( i = 0; i < 4; sc[ i++ ] = 0 );
        for( i = 0; i < 3; i++ )
            freq[ 0 ][ i ] = freq[ 1 ][ i ] = 0;
        for( i = 0, ix = 3; i < CSIZE; i++, ix *= 3 )
        {
            bzero( myh[ i ], ix * sizeof(short int) * 3 );
            bzero( oph[ i ], ix * sizeof(short int) * 3 );
        }
    }

    /* (3) Last hand of the match */

    /* Statistics -- deleted */


    /* First hand - make a random move */
    if( TRIAL <= 0 )
        JRANDOM_MOVE



    /*
     *
     * Process previous game
     *
     */

    /* (1) How is the match going? */
         if( ( MY_PLAY - YOU_PLAY ==  1 ) ||
         ( MY_PLAY - YOU_PLAY == -2 ) )
        score += 1;
    else if( ( YOU_PLAY - MY_PLAY ==  1 ) ||
         ( YOU_PLAY - MY_PLAY == -2 ) )
        score += -1;

    /* (2) Save context */
    freq[ 0 ][ ME [ TRIAL ] ]++;
    freq[ 1 ][ YOU[ TRIAL ] ]++;

    /* (3) How good are our predictions? */
    if( TRIAL > 1 )
    {
        for( i = 0; i < 4; i++ )
            if( ( ( move[ i ] + 2 ) % 3 ) == YOU_PLAY )
                sc[ i ]++;
    }

    /* (4) Update context strings */
    for( j = YOU[TRIAL], i = 1; i <= CSIZE && TRIAL-i > 0; i++ )
        oph[ i-1 ][ j += YOU[ TRIAL-i ] * 3 * mult[ i-1 ] ]++;
    for( j = YOU[TRIAL], i = 1; i <= CSIZE && TRIAL-i > 0; i++ )
        myh[ i-1 ][ j += ME [ TRIAL-i ] * 3 * mult[ i-1 ] ]++;

    /* Periodically scale back results so that the program can */
    /* switch strategies.                      */
    if( ( TRIAL % 32 ) == 0 )
    {
        for( i = 0; i < 3; i++ )
        {
            freq[ 0 ][ i ] >>= 1;
            freq[ 1 ][ i ] >>= 1;
        }
        for( i = 0; i < 4; sc[ i++ ] >>= 1 );
    }



    /*
     *
     * Use 4 special cases and 4  prediction models
     *
     *
     */

    /* (1) First move */
    /* Taken care of above */

    /* (2) If down too far, go random */
    if( score < -WSIZE )
        JRANDOM_MOVE

    /* (3) Make a random move to confuse the opponent */
    if( gorandom )
    {
        if( (--gorandom) >= 8 )
            JRANDOM_MOVE
    }

    /* (4) If things not going well with our predicitons, make */
    /* random moves for a while to confuse the opponent        */
    if( score <= -10 && gorandom == 0 )
    {
        gorandom = 16;
        JRANDOM_MOVE
    }

    /* (5) Use tables to predict next move using opponent info */
    /* Prediction 1                                            */
    BiopicWeight( wt, oph, YOU );
    move[ 0 ] = BiopicMove( wt );

    /* (6) Use tables to predict next move using our info   */
    /* Prediction 2                                         */
    BiopicWeight( wt, myh, ME );
    move[ 1 ] = BiopicMove( wt );

    /* (7) Check the frequency of the opponent's actions    */
    /* Prediction 3                                         */
    move[ 2 ] = BiopicMove( &freq[ 0 ][ 0 ] );

    /* (8) Check the frequency of the opponent's actions    */
    /* Prediction 4                                         */
    move[ 3 ] = BiopicMove( &freq[ 1 ][ 0 ] );

    /* Finally, we decide which strategy to use             */
    /* Use maximum sc for the move                          */
    for( j = 0, i = 1; i < 4; i++ )
        if( sc[ i ] > sc[ j ] )
            j = i;
    /* Ta da */
    return( move[ j ] );
}
/**********************************************************************/


/*  Entrant:  Simple Modeller (7)   Don Beal (UK)

 The simple predictor counts the number of times r/p/s occurred
 after each of the possible move events.  In addition to the 9
 possible r/p/s combinations for the two players, counts are kept
 ignoring the player move, ignoring the opponent move, or both,
 leading to 16 sets of counts.  The predictor then selects the
 count set that has the most extreme distribution, and plays
 against that.  The play against a given distribution is obtained
 by calculating the expected return of each play, and selecting the
 play with the best return.
 
 The idea to select the most extreme distribution (instead of the
 distribution in which we have the greatest confidence) was an
 experiment - I thought it might promote information gathering
 plays, and aggressively exploit easily-predictable opponents
 earlier than cautious approaches would.  It had the accidental
 advantage of being harder to predict!
 
 The simple modeller keeps the same information as the simple
 predictor, but for both players.  It can therefore counter an
 opponent using a similar counting technique.  To choose the count
 set to play against, the simple modeller keeps track of past
 performance (the score we would have if we had used that count set
 for all the moves so far).  The simple modeller then plays against
 the count set with the highest score.  If no count set shows a
 positive score, it plays at random.
 
 Both programs exponentially decay their memory of past plays to
 improve performance against opponents who change their strategy
 over time.
 
 [Both programs were written hastily and not very readably - sorry
 about that!]
  --
  Don Beal
*/

int mod1bot()  /* Don Beal (UK) simple model builder */
{   static double c[96], d[96], fade=0.98;
    static double c0,c1,c2,u0,u1,u2,b;  int bm;
#define SETC(x) c0=c[x];c1=c[x+1];c2=c[x+2];
#define SETD(x) c0=d[x];c1=d[x+1];c2=d[x+2];
#define SETU u0=c2-c1;u1=c0-c2;u2=c1-c0;
#define SETBM b=u0;bm=0;if(u1>b){b=u1;bm=1;};if(u2>b){b=u2;bm=2;}
#define BEATBM bm=(bm+1)%3;
#define SCORE(m,o) (m==o?0:(((o+1)%3)==m?1:-1))
    int i,j,k,l,m,m1,o,o1, s, id;
    double q, qi, qj, qk, ql, qd;
    int history_length= my_history[0];
    m = 0; m1 = 0; o = 0; o1 = 0; /* -db */
    if(history_length>0)
    { o = opp_history[history_length];
      m = my_history[history_length];
    }
    if(history_length>1)
    { o1 = opp_history[history_length-1];
      m1 = my_history[history_length-1];
    }
    if(history_length==0)
    { for(i=0;i<96;i++) c[i]=d[i]=0;   }
    if(history_length>1)
    { i=o1*24+m1*6; j=o1*24+3*6; k=3*24+m1*6; l=3*24+3*6;
      if(history_length>2)
      { if(c[i+3]>0)
                /* c[i+4]+=score(bplay(&c[i]),o); */
          { SETC(i); SETU; SETBM; c[i+4]+=SCORE(bm,o); c[i+5]+=1; }
        if(c[j+3]>0)
          { SETC(j); SETU; SETBM; c[j+4]+=SCORE(bm,o); c[j+5]+=1; }
        if(c[k+3]>0)
          { SETC(k); SETU; SETBM; c[k+4]+=SCORE(bm,o); c[k+5]+=1; }
        if(c[l+3]>0)
          { SETC(l); SETU; SETBM; c[l+4]+=SCORE(bm,o); c[l+5]+=1; }
      }
      c[i+o]+=1;  c[j+o]+=1;  c[k+o]+=1; c[l+o]+=1;
      c[i+3]+=1;  c[j+3]+=1;  c[k+3]+=1; c[l+3]+=1;
      i=m1*24+o1*6; j=m1*24+3*6; k=3*24+o1*6; l=3*24+3*6;
      if(history_length>2)
      { if(d[i+3]>0)
                /* md=bplay(&d[i]); d[i+4]+=score((md+1)%3,o); */
          { SETD(i); SETU; SETBM; BEATBM; d[i+4]+=SCORE(bm,o); d[i+5]+=1; }
        if(d[j+3]>0)
          { SETD(j); SETU; SETBM; BEATBM; d[j+4]+=SCORE(bm,o); d[j+5]+=1; }
        if(d[k+3]>0)
          { SETD(k); SETU; SETBM; BEATBM; d[k+4]+=SCORE(bm,o); d[k+5]+=1; }
        if(d[l+3]>0)
          { SETD(l); SETU; SETBM; BEATBM; d[l+4]+=SCORE(bm,o); d[l+5]+=1; }
      }
      d[i+m]+=1;  d[j+m]+=1;  d[k+m]+=1; d[l+m]+=1;
      d[i+3]+=1;  d[j+3]+=1;  d[k+3]+=1; d[l+3]+=1;
    }
    if(history_length>50)
      for(i=0;i<96;i++) { c[i]=c[i]*fade;  d[i]=d[i]*fade; }
    if(history_length==0)   return( random() % 3 );
    else if(history_length==1)    return( (o+1) % 3 );
    else
    { id=m*24+o*6;  SETD(id); SETU; SETBM; BEATBM;
      qd= d[id+5]>0? d[id+4]/d[id+5]:0;
      i=o*24+m*6; j=o*24+3*6; k=3*24+m*6; l=3*24+3*6;
      qi= c[i+5]>0? c[i+4]/c[i+5]:0;
      qj= c[j+5]>0? c[j+4]/c[j+5]:0;
      qk= c[k+5]>0? c[k+4]/c[k+5]:0;
      ql= c[l+5]>0? c[l+4]/c[l+5]:0;
      q=qi; s=i;
      if(qj>q) { q=qj; s=j; }
      if(qk>q) { q=qk; s=k; }
      if(ql>q) { q=ql; s=l; }
      if(qd>q && qd>0) return(bm);
      SETC(s); SETU; SETBM;
      if(q>0) return(bm);
      return( random()%3 );
    }
#undef SETC
#undef SETD
#undef SETU
#undef SETBM
#undef BEATBM
#undef SCORE
}
/**********************************************************************/


/*  Entrant:  Simple Predictor (14)   Don Beal (UK)  */

int predbot()
{
    static double c[64];  int history_length= my_history[0];
    int i,j,k,l,m,m1,o,o1, s,mr,mp,ms,mb;
    double q, qi, qj, qk, ql;
    if(history_length==0)
    { for(i=0;i<64;i++) c[i]=0;
      return( random() % 3 );
    }
    else {
    o = opp_history[history_length];
    m = my_history[history_length];
    if(history_length>1)
    { o1 = opp_history[history_length-1];
      m1 = my_history[history_length-1];
      i=o1*16+m1*4+o; j=o1*16+3*4+o; k=3*16+m1*4+o; l=3*16+3*4+o;
      c[i]+=1;  c[j]+=1;  c[k]+=1; c[l]+=1;
      c[i+3-o]+=1;  c[j+3-o]+=1;  c[k+3-o]+=1; c[l+3-o]+=1;
    }
    for(i=0;i<64;i++) c[i]=c[i]*0.98;
    i=o*16+m*4; j=o*16+3*4; k=3*16+m*4; l=3*16+3*4;
    for(qi=c[i],m=1;m<3;m++) if(c[i+m]>qi) qi=c[i+m];  qi=qi/c[i+3];
    for(qj=c[j],m=1;m<3;m++) if(c[j+m]>qj) qj=c[j+m];  qj=qj/c[j+3];
    for(qk=c[k],m=1;m<3;m++) if(c[k+m]>qk) qk=c[k+m];  qk=qk/c[k+3];
    for(ql=c[l],m=1;m<3;m++) if(c[l+m]>ql) ql=c[l+m];  ql=ql/c[l+3];
    q=qi; s=i;
    if(qj>q) { q=qj; s=j; }
    if(qk>q) { q=qk; s=k; }
    if(ql>q) { s=l; }
    mr= c[s+2]-c[s+1];
    mp= c[s]-c[s+2];
    ms= c[s+1]-c[s];
    mb=mr;  m=rock;
    if(mp>mb) { mb=mp;  m=paper; }
    if(ms>mb) m=scissors;
    return(m);
    }
}
/**********************************************************************/


/*  Entrant:  Robertot (8)   Andreas Junghanns (Ger)  */

int robertot ()
{
#define NHIST           10
#define NPREDICTS       2
#define STEPS           200     /* grains for the freq count % */
#define MAXVOTE         256     /* maximal vote for 0/100% */
#define ZERO            11.1    /* zero point for the distribution */

#define FUNC(x) ((x)*(x)*(x)*(x)*(x))
#define MAXR(x,y) ((x)>(y)?(x):(y))
#define MINR(x,y) ((x)<(y)?(x):(y))

    /* gather stats for counts of related events, NHIST back */
    static int hitsd[NHIST][3][3][3];   /* NHIST counts, for each combination */
    static int countd[NHIST][3][3];     /* history was seen how many times */
    int p,h,pos,rsb,h_rsb,o_rsb;
    int vote[3];
    static int incvote[STEPS+1];
    float index;

    if (opp_history[0] == 0) {
        memset(hitsd,0,sizeof(int)*NHIST*3*3*3);
        memset(countd,0,sizeof(int)*NHIST*3*3);
        for (index=((float)MAXVOTE)/FUNC(ZERO), p=0, h=ZERO; h>0; h--)
                incvote[p++] = -((int)((((float)FUNC(h))*index)+0.5));
        for (index=((float)MAXVOTE)/FUNC(STEPS-ZERO), h=ZERO; h<=STEPS; h++)
                incvote[p++] = ((int)((((float)FUNC(h-ZERO))*index)+0.5));
    }
    if (opp_history[0] >= NPREDICTS) {
        /* Only with enough data try to predict! */
        pos = opp_history[0];
        rsb = opp_history[pos];
        for (h=0; h<NHIST && (pos-(h+1))>0; h++) {
            countd[h][opp_history[pos-(h+1)]][my_history[pos-(h+1)]]++;
            hitsd [h][rsb][opp_history[pos-(h+1)]][my_history[pos-(h+1)]]++;
        }
        for (rsb=0; rsb<3; rsb++) vote[rsb]=0;
        /* Now, each history entry will vote for which move to play */
        for (rsb=0; rsb<3; rsb++) {
            for (h=0; h<NHIST && (pos-h)>0; h++) {
                o_rsb = opp_history[pos-h];
                h_rsb =  my_history[pos-h];
                if (countd[h][o_rsb][h_rsb]) {
                  index=((float)STEPS)*
                          hitsd[h][rsb][o_rsb][h_rsb]/countd[h][o_rsb][h_rsb];
                  vote[rsb] += incvote[(int)index];
                }
            }
        }
        h = MINR(vote[rock],vote[paper]);
        h = MINR(h,vote[scissors]);
        vote[rock] -= h; vote[paper] -= h; vote[scissors] -= h;
        h = MAXR(vote[rock],vote[paper]);
        h = MAXR(h,vote[scissors]);
        h = (h*3)/4;
        if (h==0) h++;
        vote[rock] /= h; vote[paper] /= h; vote[scissors] /= h;
        if (verbose1)
                printf("%i %i %i\n", vote[rock], vote[paper], vote[scissors]);
        if (vote[rock] > vote[scissors] && vote[rock] > vote[paper])
            return(paper);
        else if (vote[scissors] > vote[paper] && vote[scissors] > vote[rock])
            return(rock);
        else if (vote[paper] > vote[rock] && vote[paper] > vote[scissors])
            return(scissors);
        else if (vote[rock] == vote[paper] && vote[paper] == vote[scissors])
            return( random() % 3);
        else if (vote[rock] == vote[paper])
            return(paper);
        else if (vote[paper] == vote[scissors])
            return(scissors);
        else if (vote[scissors] == vote[rock])
            return(rock);
        else return( random() % 3); /* should never happen */
    } else {
        return( random() % 3);
    }
}
/**********************************************************************/


/*  Entrant:  Boom (10)   Jack van Rijswijk (Net)  */

float boom_getrelevance(int r, int p, int s) {
  float best;

  best = s-p;
  if (r-s > best) best = r-s;
  if (p-r > best) best = p-r;

  return (best/(r+p+s+5));
}

int boom_rotate (int rps, int increment) {
  rps = (rps+increment) % 3;
  if (rps < 0) rps += 3;
  return(rps);
}

int boom_rps_result (int action1, int action2) {
  if (action1 == action2) return(0);
  if (boom_rotate(action1,1) == action2) return(-1);
  return(1);
}

int boom () {
  int boom_history = 27;
  float lambda = 0.95;

  static int boom_stats[28][4][4][3];
  int boom_secondary_stats[28][4][4][3];
  static int boom_overall;
  static int boom_gear;
  static float boom_gear_success[3];
  static float boom_recent_success;

  float bail_min,bail_max,bail;
  float bail_l_min,bail_l_max,bail_l_diff;

  int turn, action;
  int i,j;
  int opp_earlier,my_earlier,opp_last,my_last;
  float best,pred_r,pred_p,pred_s;

  int filter_opp, filter_me, filter_lag;
  
  pred_r = 0; pred_p = 0; pred_s = 0;
  filter_opp = 0; filter_me = 0; filter_lag = -1;
  turn = opp_history[0];

  bail_l_min = sqrt((1-lambda)/3);
  bail_l_max = sqrt(2*(1-lambda));
  bail_l_diff = bail_l_min - bail_l_max;

  if (turn == 0) { /* initialize arrays */
    int k,l;
    for (i=0; i<boom_history; i++) for (j=0; j<4; j++) for (k=0; k<4; k++)
      for (l=0; l<3; l++) boom_stats[i][j][k][l] = 0;
    boom_overall = 0;
    boom_gear = 0;
    for (i=0; i<3; i++) boom_gear_success[i] = 0;
    boom_recent_success = 0;
  }
  else { /* update statistics */

    opp_last = opp_history[turn];
    my_last = my_history[turn];

    for (i=0; i<boom_history; i++) {
      if (turn-i-1 > 0) {
        opp_earlier = opp_history[turn-i-1];
        my_earlier = my_history[turn-i-1];

        boom_stats[i][opp_earlier][my_earlier][opp_last]++;
        boom_stats[i][3][my_earlier][opp_last]++;
        boom_stats[i][opp_earlier][3][opp_last]++;
        boom_stats[i][3][3][opp_last]++;
      }
    }

    for (i=0; i<3; i++) boom_gear_success[i] *= lambda;
    boom_recent_success *= lambda;

    j = boom_rps_result(my_last,opp_last); /* win/tie/loss previous turn */
    if (j == -1) {
      boom_overall--;
      boom_recent_success -= 1-lambda;
      boom_gear_success[boom_gear] -= 1-lambda;
      boom_gear_success[boom_rotate(boom_gear,-1)] += 1-lambda;
    }
    else if (j == 1) {
      boom_overall++;
      boom_recent_success += 1-lambda;
      boom_gear_success[boom_gear] += 1-lambda;
      boom_gear_success[boom_rotate(boom_gear,+1)] -= 1-lambda;
    }
    else { 
      boom_gear_success[boom_rotate(boom_gear,+1)] += 1-lambda;
      boom_gear_success[boom_rotate(boom_gear,-1)] -= 1-lambda;
    }
  }

  /* check current context */
  best = 0;

  for (i=0; i<boom_history; i++) if (i<=turn) {
    int r,p,s,t;
    float w;

    opp_earlier = opp_history[turn-i]; my_earlier = my_history[turn-i];

    r = boom_stats[i][opp_earlier][my_earlier][0];
    p = boom_stats[i][opp_earlier][my_earlier][1];
    s = boom_stats[i][opp_earlier][my_earlier][2];
    w = boom_getrelevance(r,p,s);
    if (w>best) {
      best = w; t = r+p+s;
      pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      filter_opp = opp_earlier; filter_me = my_earlier; filter_lag = i;
    }

    r = boom_stats[i][3][my_earlier][0];
    p = boom_stats[i][3][my_earlier][1];
    s = boom_stats[i][3][my_earlier][2];
    w = boom_getrelevance(r,p,s);
    if (w>best) {
      best = w; t = r+p+s;
      pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      filter_opp = 3; filter_me = my_earlier; filter_lag = i;
    }

    r = boom_stats[i][opp_earlier][3][0];
    p = boom_stats[i][opp_earlier][3][1];
    s = boom_stats[i][opp_earlier][3][2];
    w = boom_getrelevance(r,p,s);
    if (w>best) {
      best = w; t = r+p+s;
      pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      filter_opp = opp_earlier; filter_me = 3; filter_lag = i;
    }

    r = boom_stats[i][3][3][0];
    p = boom_stats[i][3][3][1];
    s = boom_stats[i][3][3][2];
    w = boom_getrelevance(r,p,s);
    if (w>best) {
      best = w; t = r+p+s;
      pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      filter_opp = 3; filter_me = 3; filter_lag = i;
    }
  }
  
  /* filter statistics, get second-order stats */
  /*    only if we're less than 95% sure so far */

  if ((best < 0.95) && (filter_lag >= 0)) { 
    int k,l,r,p,s,t;
    float w;

    /* reset 2nd order stats */
    for (i=0; i<boom_history; i++) for (j=0; j<4; j++) for (k=0; k<4; k++)
      for (l=0; l<3; l++) boom_secondary_stats[i][j][k][l] = 0;

    /* get 2nd order stats */
    for (i=filter_lag+2; i<=turn; i++) {
      opp_earlier = opp_history[i-filter_lag-1];
      my_earlier = my_history[i-filter_lag-1];
      if (((filter_opp == 3) || (filter_opp == opp_earlier)) &&
          ((filter_me == 3) || (filter_me == my_earlier))) {
        opp_last = opp_history[i];
        for (j=0; j<boom_history; j++) {
          if (i-j-1 > 0) {
            opp_earlier = opp_history[i-j-1];
            my_earlier = my_history[i-j-1];
            boom_secondary_stats[j][opp_earlier][my_earlier][opp_last]++;
            boom_secondary_stats[j][3][my_earlier][opp_last]++;
            boom_secondary_stats[j][opp_earlier][3][opp_last]++;
            boom_secondary_stats[j][3][3][opp_last]++;
          }
        }
      }
    }

    /* any better information in there? */
    for (i=0; i<boom_history; i++) if (i<turn) {
      opp_earlier = opp_history[turn-i]; my_earlier = my_history[turn-i];

      r = boom_secondary_stats[i][opp_earlier][my_earlier][0];
      p = boom_secondary_stats[i][opp_earlier][my_earlier][1];
      s = boom_secondary_stats[i][opp_earlier][my_earlier][2];
      w = boom_getrelevance(r,p,s);
      if (w>best) {
          best = w; t = r+p+s; 
          pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      }

      r = boom_secondary_stats[i][3][my_earlier][0];
      p = boom_secondary_stats[i][3][my_earlier][1];
      s = boom_secondary_stats[i][3][my_earlier][2];
      w = boom_getrelevance(r,p,s);
      if (w>best) {
        best = w; t = r+p+s;
        pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      }

      r = boom_secondary_stats[i][opp_earlier][3][0];
      p = boom_secondary_stats[i][opp_earlier][3][1];
      s = boom_secondary_stats[i][opp_earlier][3][2];
      w = boom_getrelevance(r,p,s);
      if (w>best) {
        best = w; t = r+p+s;
        pred_r = (float) r/t; pred_p = (float) p/t; pred_s = (float) s/t;
      }
    }
  }

  /* got the predicted probabilities of r-p-s -- determine suggested action */
  best = pred_s - pred_p; action = rock;
  if ((pred_r - pred_s) > best) {best = pred_r - pred_s; action = paper;}
  if ((pred_p - pred_r) > best) action = scissors;

  /* modify the action according to the gears */
  best = boom_gear_success[0]; boom_gear = 0;
  if (boom_gear_success[1] > best) {
    best = boom_gear_success[1]; boom_gear = 1;
  }
  if (boom_gear_success[2] > best) {
    best = boom_gear_success[2]; boom_gear = 2;
  }
  action = (action + boom_gear)%3;

  /* ignore the action altogether if we're losing */
  /* global bailout */
  bail_min = (float) sqrt(turn) / sqrt(3.0);
  bail_max = (float) sqrt(turn) * sqrt(2.0);
  if (bail_min < bail_max)
    bail = (float) (bail_min + boom_overall) / (bail_min - bail_max);
  else bail = 0;

  /* local bailout */
  if ((boom_recent_success + bail_l_min) / bail_l_diff > bail)
    bail = (boom_recent_success + bail_l_min) / bail_l_diff;

  if (bail < 0) bail = 0;
  if (bail > 1) bail = 1;

  /* final decision: going random this turn? */
  if (flip_biased_coin(bail))
    action = biased_roshambo((float) 1/3,(float) 1/3);

  return(action);
}
/**********************************************************************/


/*  Entrant:  Shofar (11)   Rudi Cilibrasi (USA)  */

struct strat {
    int(*pname)();
    void (*init)();
    double score;
    int ivar[16];
    double dvar[16];
    int move;
};

struct strat s[128];
int sc = 0;
int chose = -1;
struct strat *cur;

void narcissus_init() {
    static int whoiam = 0;
    cur->ivar[0] = whoiam;
    whoiam = (whoiam+1) % 3;
}

int narcissus_play() {
    int mymove = my_history[my_history[0]];
    return (cur->ivar[0] + mymove) % 3;
}

void mirror_init() {
    static int whoiam = 0;
    cur->ivar[0] = whoiam;
    whoiam = (whoiam+1) % 3;
}

int mirror_play() {
    int hermove = opp_history[opp_history[0]];
    return (cur->ivar[0] + hermove) % 3;
}

void single_init() {
    static int whoiam = 0;
    cur->ivar[0] = whoiam;
    whoiam = (whoiam+1) % 3;
}

int single_play() {
    return cur->ivar[0];
}

void pattern_init() {
    int i;
    cur->ivar[0] = 1 + random() / (maxrandom / 5);
    cur->ivar[1] = 0;
    for (i = 0; i < cur->ivar[0]; ++i)
      {
        cur->ivar[i+2] = 3*(random() / maxrandom) ;
      }
}

int pattern_play() {
    int which = cur->ivar[cur->ivar[1]+2];
    cur->ivar[1] = (cur->ivar[1]+1) % cur->ivar[0];
    return which;
}

void update_score() {
    int i;
    double worstscore = 1000;
    int worstguy;
    int hermove, winmove, losemove;
    worstguy = 0; /* -db */
    if (opp_history[0] == 0) return;
    hermove = opp_history[opp_history[0]];
    winmove = (hermove + 1) % 3;
    losemove = (hermove + 2) % 3;
    for (i = 0; i < sc; ++i)
      {
        int multiplier;
        multiplier = (i == chose) ? 4 : 3;
        if (s[i].move == winmove) s[i].score += multiplier;
        if (s[i].move == losemove) s[i].score -= multiplier;
        s[i].score *= 0.99;
      }
    for (i = 9; i < sc; ++i)
      if (s[i].score < worstscore)
        {
          worstguy = i;
          worstscore = s[i].score;
        }
    cur = s + worstguy;
    cur->init();
}

void enregister( void (*initfunc)(), int (*playfunc)())
{
    s[sc].pname = playfunc;
    s[sc].init = initfunc;
    cur = s+sc;
    cur->init();
    ++sc;
}

void shofar_init(void)
{
    int i;
    enregister(single_init, single_play);
    enregister(single_init, single_play);
    enregister(single_init, single_play);
    enregister(mirror_init, mirror_play);
    enregister(mirror_init, mirror_play);
    enregister(mirror_init, mirror_play);
    enregister(narcissus_init, narcissus_play);
    enregister(narcissus_init, narcissus_play);
    enregister(narcissus_init, narcissus_play);
    for (i = 0; i < 80; ++i)
        enregister(pattern_init, pattern_play);
    for (i = 0; i < sc; ++i)
        s[i].init();
}

int shofar(void)
{
    static int has_init = 0;
    double base=1.05;
    double total=0, r;
    int i;
    if (has_init == 0) { shofar_init(); has_init = 1; }
    update_score();
    for (i = 0; i < sc; ++i)
      {
        cur = s + i;
        cur->move = cur->pname();
        total += pow(base, s[i].score);
      }
    r = (random() / maxrandom) * total;
    for (i = 0; i < sc; ++i)
      {
        r -= pow(base, s[i].score);
        if (r <= 0) break;
      }
    assert(i >= 0 && i < sc);
    chose = i;
/*      printf("Her move was %d, my move was %d\n", opp_history[opp_history[0]], s[chose].move); */
    return s[chose].move;
}

/* naivete - poor roshambo player, written by cstone@pobox.com */
#define THRESH_BIGOM 0.42
#define THRESH_OKBEDUMB 0.75

enum { ROCK=0, PAPER, SCISSORS };

int triprescalc(int *x) {
    return((1<<*x)|(1<<*(x+1))|(1<<*(x+2)));
}

int win(int x) {
    if(x == ROCK) return PAPER;
    if(x == PAPER) return SCISSORS;
    return ROCK;
}

int filcompltrip(int *x) {
    int c=0;

    c=(1<<*x)|(1<<*(x+1));
    if((c^(1<<ROCK)) == 7) return ROCK;
    if((c^(1<<PAPER)) == 7) return PAPER;
    return SCISSORS;
}

int copychecklast(int offset) {

    if(opp_history[my_history[0]]==win(my_history[0]+offset)) 
        return(1);
    else return(0);
}

int naivete(void)
{
    /* imperative flags */
    static unsigned int c_trseqrpt, c_trresrpt, f_notwoseq, f_nothreeseq,
                                                f_bigom, f_okbedumb;
    static int f_cpyoffset=0, om=0;
    static float oc[3], pcts[3], tots[3], avgs[3];
    int tempint0, tempint1;
    float tempfloat0;

    if(my_history[0]==0) 
        c_trseqrpt=c_trresrpt=f_notwoseq=f_nothreeseq=f_bigom=f_cpyoffset=
          om=oc[0]=oc[1]=oc[2]=pcts[0]=pcts[1]=pcts[2]=tots[0]=tots[1]=
          tots[2]=avgs[0]=avgs[1]=avgs[2]=0;

    if(my_history[0]<=3) 
        return(SCISSORS);

    tempint0=triprescalc(&opp_history[my_history[0]-2]);

    if(opp_history[my_history[0]]==ROCK) oc[ROCK]++;
    if(opp_history[my_history[0]]==PAPER) oc[PAPER]++;
    if(opp_history[my_history[0]]==SCISSORS) oc[SCISSORS]++;

    switch(tempint0) {

    case 1:
    case 2:
    case 4:
        c_trseqrpt++;
        break;
    case 7:
        c_trresrpt++;
        break;
    default:
        c_trseqrpt=c_trresrpt=0;
        break;
    }

    if(c_trseqrpt > 2) 
        return(win(opp_history[my_history[0]-2]));

    if(c_trresrpt > 2)
        return(win(filcompltrip(&opp_history[my_history[0]-1])));

    if(!(my_history[0] % 3)) {
        if(f_cpyoffset && !copychecklast(f_cpyoffset))
            f_cpyoffset=0;
        }

        if(f_bigom && !(my_history[0] && 7)) {
            if(f_bigom >= THRESH_OKBEDUMB)
                f_okbedumb=1;
            else
                f_okbedumb=0;
        }

        if(!(my_history[0] % 23)) {
            int i;

            f_cpyoffset=0;
            for(i=0;i>=-4;i--) {
              if((opp_history[my_history[0]]==win(my_history[my_history[0]+i])) &&
                 (opp_history[my_history[0]-1]==win(my_history[my_history[0]+i-1])) &&
                 (opp_history[my_history[0]-2]==win(my_history[my_history[0]+i-2])) &&
                 (opp_history[my_history[0]-3]==win(my_history[my_history[0]+i-3])))
                 f_cpyoffset=i;
            }
        }
        /* i don't like this */
        if(!(my_history[0] % 27)) {
            int i=my_history[0]-26;
            f_notwoseq=f_nothreeseq=1;
            for(;i<=my_history[0];i++) 
                if(opp_history[i-1] == opp_history[i]) {
                    if((i<my_history[0])&&(opp_history[i]==opp_history[i+1])){
                        f_nothreeseq=0;
                        f_notwoseq=0;
                        break;
                    } else
                      f_notwoseq=0;
                }
        }
        if(!(my_history[0]%10)) {
            tempfloat0=my_history[0];

            if(my_history[0] > 10) {
                avgs[0]=tots[0]/((my_history[0]-10)/10);
                avgs[1]=tots[1]/((my_history[0]-10)/10);
                avgs[2]=tots[2]/((my_history[0]-10)/10);
            }
            tots[0]+=(pcts[0]=oc[0]/tempfloat0);
            tots[1]+=(pcts[1]=oc[1]/tempfloat0);
            tots[2]+=(pcts[2]=oc[2]/tempfloat0);
        }

        if(f_cpyoffset) 
            return(win(win(my_history[my_history[0]])));

        if(oc[ROCK] >= oc[PAPER]) {
            if((oc[SCISSORS] > oc[PAPER]) && (oc[SCISSORS] > oc[ROCK])) om=SCISSORS;
            else om=ROCK;
        } else {
            if(oc[SCISSORS] > oc[PAPER]) om = SCISSORS;
            else om=PAPER;
        }
        tempfloat0=my_history[0];
        if((my_history[0] > 30) && (oc[om]/tempfloat0 > THRESH_BIGOM)) 
            f_bigom=1;
        else
            f_bigom=0;

        switch(my_history[0] % 6) {

        case 4:
            if(f_bigom) {
                tempint0=win(om);
                break;
            }
            if(!(my_history[0] % 16)) {
                tempint0=win(om);
                break;
            }  

        case 5:
            tempint1=om;
            if((pcts[0]-avgs[0]) < (pcts[1]-avgs[1])) 
                tempint1=0;
            else
                tempint1=1;
            if((pcts[2]-avgs[2]) < (pcts[tempint1]-avgs[tempint1]))
                tempint1=2;

            tempint0=win(tempint1);
            break;
                
        case 3:
            if(my_history[0] % 12)
                tempint0=win(win(om));
            tempint0=win(om);
            break;

        case 2:
            if(f_bigom)
                tempint0=win(om);
            else            
                tempint0=win(my_history[my_history[0]]);
            break;

        case 1:
            if(f_okbedumb)
                tempint0=win(om);
            else
                tempint0=win(opp_history[my_history[0]]);
            break;

        case 0:
            tempint0=win(om);
            break;
        }       
        if(f_notwoseq && (tempint0==win(opp_history[my_history[0]])))
            tempint0=win(tempint0);
        
        if(f_nothreeseq && 
             (opp_history[my_history[0]] == opp_history[my_history[0]-1]) &&
             (tempint0==win(opp_history[my_history[0]])))
            tempint0=win(tempint0);      
                
        return(tempint0);
}
/**********************************************************************/


/*  Entrant:  ACT-R Lag2 (13)   Dan Bothell, C Lebiere, R West (USA)

 RoShamBo player submission by Christian Lebiere, Robert West, 
 and Dan Bothell 
 
 This player is based on an ACT-R (http://act.psy.cmu.edu) model
 that plays RoShamBo.  The model can be played against on the web 
 at http://act.psy.cmu.edu/ACT/ftp/models/RPS/index.html.
 
 suggested name "ACT-R Lag2"
 function name actr_lag2_decay
*/
/*
  C function that implements the math underlying the
  ACT-R (http://act.psy.cmu.edu) model of RPS by 
  Christian Lebiere and Robert West (Published in the 
  Proceedings of the Twenty-first Conference of the 
  Cognitive Science Society.)
  This model stores in long-term memory sequences of 
  moves and attempts to anticipate the opponent's 
  moves by retrieving from memory the most active sequence. 
  More information, and a web playable version avalable at:
  http://act.psy.cmu.edu/ACT/ftp/models/RPS/index.html
*/
int actr_lag2_decay (void)
{
  double frequencies[3],score,p,best_score=maxrandom;
 
  int back1 = 0,back2 = 0,i,winner,index=my_history[0];
        
  winner = 0; /* -db */
  for(i=0;i<3;i++)
     frequencies[i]=pow(index + 1,-.5);
 
  if (index >= 2)
  {
     back2=opp_history[index - 1];
     back1=opp_history[index];
  }
 
  for(i=0;i<index;i++)
  {
     if (i >= 2 && opp_history[i - 1] == back2 && opp_history[i] == back1)
       frequencies[opp_history[i + 1]] +=  pow(index - i, -0.5); 
  }
                
  for (i=0;i<3;i++)
  {
     /*
      Approximates a sample from a normal distribution with mean zero
      and s-value of .25 [s = sqrt(3 * sigma) / pi]
     */
      
     do
     {
       p=random();
     }while(p == 0.0);
 
     p /= maxrandom;
     p= .25 * log ((1 - p) / p);
 
     /* end of noise calculation */
     score = p + log(frequencies[i]);
        
     if (best_score == maxrandom || score > best_score)
     {
       winner=i;
       best_score = score;
     }
  }
   return ((winner + 1) % 3);
}       
/**********************************************************************/


/*  Entrant:  Majikthise (15)   Markian Hlynka (Can)  */

int markov5 ()
{
#define markovLength 243
  /* This bot is designed to win the current match. */

    int i,j;
    int markovindex;
    int nonzeros;
    int score;
    double newprob, cumprob;
    int retval;     /* the value to return */
    static int windowSize=5;
    /* int markovLength=9; */ /*3^size*/
    static int wins, losses;
    static double percentWins,percentLosses, margin;

    static double MarkovChain[markovLength][3];
    static int Markovuse[markovLength];
    static int MarkovTally[markovLength][3];

    retval = 0; /* -db */
    if (my_history[0]==0)   /* if we're just starting, init the array. */
    {
        for(i=0;i<markovLength;i++)         /* for every row */
        {
            Markovuse[i]=0;
            for(j=0;j<3;j++)            /* reset every column */
            {
              MarkovChain[i][j]=0.33;
              MarkovTally[i][j]=0;
            }
        }
        /* now set our watch vars and stats accumulators */
    wins=losses=0;
    percentWins=percentLosses=margin=0;

    }
    else
    {
      /* check if we won or lost on the last turn */
        if ((opp_history[opp_history[0]]+1)%3 == my_history[my_history[0]])
            wins++;
        else if ((opp_history[opp_history[0]]+2)%3 == my_history[my_history[0]])
            losses++;

        /* accumulate our stats       */
        percentWins = (double)wins/(double)my_history[0];
        percentLosses = (double)losses/(double)my_history[0];
    }/* else */

    /*******This is where we update the markov chain**************/

    /* regardless, update the markov chain. */

    if(opp_history[0]>windowSize)       /* if we're past P1.. remember, P1=P0 */
    {
        markovindex=0;
        for(i=windowSize;i>=1;i--)
            markovindex+=((i==1)?
                (opp_history[opp_history[0]-i]):(opp_history[opp_history[0]-i]*3));

        /* now if we haven't used the row before, zero it and put a one in the */
        /* right place */
        if (!Markovuse[markovindex])
        {
            Markovuse[markovindex]=1;
            for(j=0;j<3;j++)
                MarkovChain[markovindex][j]=0;
            MarkovChain[markovindex][opp_history[opp_history[0]]]=1.0;
            MarkovTally[markovindex][opp_history[opp_history[0]]]++;
        }/* if */
        else /* ah. it's been used before, so now we distribut it across all used ones. */
        {/* duh. don't forget to check that this is a new one */
            MarkovTally[markovindex][opp_history[opp_history[0]]]++;

            nonzeros=0;

            /* count how many have been used (are non-zero). */
            for(j=0;j<3;j++)
                nonzeros+=MarkovTally[markovindex][j];
            /* add one */
            newprob=1.0/((double)nonzeros);
                
            /* distribute that value among them. */
            for(j=0;j<3;j++)
              if (MarkovTally[markovindex][j]>0)
                MarkovChain[markovindex][j]=newprob*(double)MarkovTally[markovindex][j];
        }/* else */

    }

    /**********************/

    margin=percentWins-percentLosses;
    score=wins-losses;

    /* if we're more that 60% behind or ahead, bail. also, if we haven't done */
    /* even one move, don't use the markov chain if we don't have a previous */
    /* move to look up. */
    if ((my_history[0]<=windowSize)/*||(score<-50)*/)
        retval=(biased_roshambo(0.33333,0.33333));

    else
    {
      /* if we didn't bail, we use the markov chain */
      /* for now use random */
      /* retval=(biased_roshambo(0.33333,0.33333)); */

        markovindex=0;
        for(i=windowSize-1;i>=0;i--)
            markovindex+=((i==0)?
                (opp_history[opp_history[0]-i]):(opp_history[opp_history[0]-i]*3));

        /* generate a continuous uniform variate */
        newprob=random()/maxrandom;
        /* now do a cumulative probability. */
        cumprob=0;
        for(j=0;j<3;j++)
        {
            cumprob+=MarkovChain[markovindex][j];
            if (newprob<cumprob)
            {
                retval=(j+1)%3;
                break;
            }
        }/* for */
        if(!(newprob<cumprob))  /* test to make sure we don't have floating point error */
            retval=0; /*((2+1)%3)*/
    }

    return(retval);
}
/**********************************************************************/


/*  Entrant:  Vroomfondel (18)   Markian Hlynka (Can)  */

int markovbails ()
{
#define markovLength 243
  /* This bot is designed to win the current match. */

    int i,j;
    int markovindex;
    int nonzeros;
    int score;
    double newprob, cumprob;
    int retval;     /* the value to return */
    static int windowSize=5;
    /* int markovLength=9; */ /*3^size*/
    static int wins, losses;
    static double percentWins,percentLosses, margin;

    static double MarkovChain[markovLength][3];
    static int Markovuse[markovLength];
    static int MarkovTally[markovLength][3];

    retval = 0; /* -db */
    if (my_history[0]==0)   /* if we're just starting, init the array. */
    {
        for(i=0;i<markovLength;i++)         /* for every row */
        {
            Markovuse[i]=0;
            for(j=0;j<3;j++)            /* reset every column */
            {
              MarkovChain[i][j]=0.33;
              MarkovTally[i][j]=0;
            }
        }
        /* now set our watch vars and stats accumulators */
    wins=losses=0;
    percentWins=percentLosses=margin=0;

    }
    else
    {
      /* check if we won or lost on the last turn */
        if ((opp_history[opp_history[0]]+1)%3 == my_history[my_history[0]])
            wins++;
        else if ((opp_history[opp_history[0]]+2)%3 == my_history[my_history[0]])
            losses++;

        /* accumulate our stats       */
        percentWins = (double)wins/(double)my_history[0];
        percentLosses = (double)losses/(double)my_history[0];
    }/* else */

    /*******This is where we update the markov chain**************/

    /* regardless, update the markov chain. */

    if(opp_history[0]>windowSize)       /* if we're past P1.. remember, P1=P0 */
    {
        markovindex=0;
        for(i=windowSize;i>=1;i--)
            markovindex+=((i==1)?
                (opp_history[opp_history[0]-i]):(opp_history[opp_history[0]-i]*3));

        /* now if we haven't used the row before, zero it and put a one in the */
        /* right place */
        if (!Markovuse[markovindex])
        {
            Markovuse[markovindex]=1;
            for(j=0;j<3;j++)
                MarkovChain[markovindex][j]=0;
            MarkovChain[markovindex][opp_history[opp_history[0]]]=1.0;
            MarkovTally[markovindex][opp_history[opp_history[0]]]++;
        }/* if */
        else /* ah. it's been used before, so now we distribut it across all used ones. */
        {/* duh. don't forget to check that this is a new one */
            MarkovTally[markovindex][opp_history[opp_history[0]]]++;

            nonzeros=0;

            /* count how many have been used (are non-zero). */
            for(j=0;j<3;j++)
                nonzeros+=MarkovTally[markovindex][j];
            /* add one */
            newprob=1.0/((double)nonzeros);
                
            /* distribute that value among them. */
            for(j=0;j<3;j++)
              if (MarkovTally[markovindex][j]>0)
                MarkovChain[markovindex][j]=newprob*(double)MarkovTally[markovindex][j];
        }/* else */

    }

    /**********************/

    margin=percentWins-percentLosses;
    score=wins-losses;

    /* if we're more that 60% behind or ahead, bail. also, if we haven't done */
    /* even one move, don't use the markov chain if we don't have a previous */
    /* move to look up. */
    if ((my_history[0]<=windowSize)||(score<-50))
        retval=(biased_roshambo(0.33333,0.33333));

    else
    {
      /* if we didn't bail, we use the markov chain */
      /* for now use random */
      /* retval=(biased_roshambo(0.33333,0.33333)); */

        markovindex=0;
        for(i=windowSize-1;i>=0;i--)
            markovindex+=((i==0)?
                (opp_history[opp_history[0]-i]):(opp_history[opp_history[0]-i]*3));

        /* generate a continuous uniform variate */
        newprob=random()/maxrandom;
        /* now do a cumulative probability. */
        cumprob=0;
        for(j=0;j<3;j++)
        {
            cumprob+=MarkovChain[markovindex][j];
            if (newprob<cumprob)
            {
                retval=(j+1)%3;
                break;
            }
        }/* for */
        if(!(newprob<cumprob))  /* test to make sure we don't have floating point error */
            retval=0; /*((2+1)%3)*/
    }

    return(retval);
}
/**********************************************************************/


/*  Entrant:  Granite (17)   Aaron Davidson (Can)  */


/**************************************************************
 * GRANITE 1.3 By Aaron Davidson, Sept. 1999                  *
 * davidson@cs.ualberta.ca                                    *
 **************************************************************/

#define DEPTH            3
#define NUM_RECENT      20

#define RAND_FLOAT (random() / maxrandom) 
#define RAND_INT(x)   (int)((RAND_FLOAT * (x)))

int granite() {
    int i,j,k,m,r,p,s;
    float noise,pR,pP,pS;

    /* persistent tallies of contextual frequencies */
    static int p_opp_0[3];              static int p_my_0[3];
    static int p_opp_1[3][3];           static int p_my_1[3][3];
    static int p_opp_2[3][3][3];        static int p_my_2[3][3][3];
    static int p_oppmy_2[3][3][3];      static int p_myopp_2[3][3][3];
    static int p_opp_3[3][3][3][3];     static int p_my_3[3][3][3][3];

    static int my_wins; static int opp_wins;

    /* number of games played */
    int ng = opp_history[0]; 

    int oL = opp_history[ng];    
    int oL1 = opp_history[ng-1];    
    int oL2 = opp_history[ng-2];    
    int oL3 = opp_history[ng-3];    

    int mL = my_history[ng];    
    int mL1 = my_history[ng-1];    
    int mL2 = my_history[ng-2];    
    int mL3 = my_history[ng-3];    

    /********************************************/

    /* FIRST MOVE -- INIT ARRAYS */
    if (ng == 0) {
        my_wins = 0; opp_wins = 0;
        for (i=0;i<3;i++) {
            p_opp_0[i] = 0; p_my_0[i] = 0;
            for (j=0;j<3;j++) {
                p_opp_1[i][j] = 0; p_my_1[i][j] = 0;
                for (k=0;k<3;k++) {
                    p_opp_2[i][j][k] = 0; p_my_2[i][j][k] = 0;
                    p_oppmy_2[i][j][k] = 0; p_myopp_2[i][j][k] = 0;
                    for (m=0;m<3;m++) {
                        p_opp_3[i][j][k][m] = 0; p_my_3[i][j][k][m] = 0;
                    }
                }
            }
        }
        return( RAND_INT(3));
    }

    my_wins = 0;
    opp_wins = 0;
    for (i=ng;i>0&&i>ng-NUM_RECENT;i--) {
        oL = opp_history[i];
        mL = my_history[i];
        if ((oL == rock && mL == paper) || (oL == paper && mL == scissors) || 
            (oL == scissors && mL == rock)) {
            my_wins++;
        } else if ((oL == rock && mL == scissors) || (oL == paper && mL == rock) ||
        (oL == scissors && mL == paper)) {
            opp_wins++;
        }
    }
    oL = opp_history[ng];
    mL = my_history[ng];


    noise = (float)(opp_wins/NUM_RECENT);


    /* TABULATE OVERALL FEQUENCY OF ACTIONS */
    p_opp_0[oL]++;
    p_my_0[mL]++;

    r = p_opp_0[rock]; p = p_opp_0[paper]; s = p_opp_0[scissors];

    /* GET FREQUENCIES OF ACTIONS FOLLOWING OUR LAST MOVES */
    if (ng > 1) { /* DEPTH == 1 */
        ++p_opp_1[oL][oL1];
        ++p_my_1[oL][mL1];
        r += p_opp_1[rock][oL] + p_my_1[rock][mL];
        p += p_opp_1[paper][oL] + p_my_1[paper][mL];
        s += p_opp_1[scissors][oL] + p_my_1[scissors][mL];
                
        if (ng > 2 && DEPTH >= 2) { /* DEPTH == 2 */
            ++p_opp_2[oL][oL1][oL2];
            ++p_my_2[oL][mL1][mL2];
            ++p_oppmy_2[oL][oL1][mL2];
            ++p_myopp_2[oL][mL1][oL2];
        
            r += p_opp_2[rock][oL][oL1] + p_my_2[rock][mL][mL1] + p_oppmy_2[rock][oL][mL1] + p_myopp_2[rock][mL][oL1];
            p += p_opp_2[paper][oL][oL1] + p_my_2[paper][mL][mL1] + p_oppmy_2[paper][oL][mL1] + p_myopp_2[paper][mL][oL1];
            s += p_opp_2[scissors][oL][oL1] + p_my_2[scissors][mL][mL1] + p_oppmy_2[scissors][oL][mL1] + p_myopp_2[scissors][mL][oL1];
            
            if (ng > 3 && DEPTH >= 3) { /* DEPTH == 3 */
            ++p_opp_3[oL][oL1][oL2][oL3];
            ++p_my_3[oL][mL1][mL2][mL3];
            
                r += p_opp_3[rock][oL][oL1][oL2] + p_my_3[rock][mL][mL1][mL2];
                p += p_opp_3[paper][oL][oL1][oL2] + p_my_3[paper][mL][mL1][mL2];
                s += p_opp_3[scissors][oL][oL1][oL2] + p_my_3[scissors][mL][mL1][mL2];
            }
        }
    } 

    pR = r/(float)(r+p+s);
    pP = p/(float)(r+p+s);
    pS = s/(float)(r+p+s);

    if (pR > pP && pR > pS) { /* predict rock */
        if (flip_biased_coin(noise*pS)) return rock;
        else if (flip_biased_coin(noise*pP)) return scissors;
        else return paper;
    } else if (pP > pR && pP > pS) { /* predict paper */
        if (flip_biased_coin(noise*pS)) return rock;
        else if (flip_biased_coin(noise*pR)) return paper;
        else return scissors;
    } else if (pS > pP && pS > pR) { /* predict scissors */
        if (flip_biased_coin(noise*pR)) return paper;
        else if (flip_biased_coin(noise*pP)) return scissors;
        else return rock;
    } else if (pR == pS && pR == pP) {
        return(RAND_INT(3));
    } else if (pR == pP) {
        if (flip_biased_coin(noise*pS)) return rock;
        return biased_roshambo(0.5,0.5);
    } else if (pR == pS) {
        if (flip_biased_coin(noise*pP)) return scissors;
        return biased_roshambo(0.5,0.0);
    } else if (pS == pP) {
        if (flip_biased_coin(noise*pR)) return paper;
        return biased_roshambo(0.0,0.5);
    }
    return (RAND_INT(3));
}
/**********************************************************************/


/*  Entrant:  Marble (19)   Aaron Davidson (Can)  */

/**************************************************************
 * MARBLE  1.4 By Aaron Davidson, Sept. 1999                  *
 * davidson@cs.ualberta.ca                                    *
 **************************************************************/

#define adDEPTH            3
#define adNUM_RECENT      20

#define adRAND_FLOAT (random() / maxrandom) 
#define adRAND_INT(x)   (int)((adRAND_FLOAT * (x)))

int marble() {
    int i,j,k,m,r,p,s;
    float noise,pR,pP,pS;

    /* persistent tallies of contextual frequencies */
    static int p_opp_0[3];              static int p_my_0[3];
    static int p_opp_1[3][3];           static int p_my_1[3][3];
    static int p_opp_2[3][3][3];        static int p_my_2[3][3][3];
    static int p_oppmy_2[3][3][3];      static int p_myopp_2[3][3][3];
    static int p_opp_3[3][3][3][3];     static int p_my_3[3][3][3][3];

    static int last_pred = -1;
    static int wins;

    /* number of games played */
    int ng = opp_history[0]; 

    int oL = opp_history[ng];    
    int oL1 = opp_history[ng-1];    
    int oL2 = opp_history[ng-2];    
    int oL3 = opp_history[ng-3];    

    int mL = my_history[ng];    
    int mL1 = my_history[ng-1];    
    int mL2 = my_history[ng-2];    
    int mL3 = my_history[ng-3];    

    /********************************************/

    /* FIRST MOVE -- INIT ARRAYS */
    if (ng == 0) {
        wins = 0;
        for (i=0;i<3;i++) {
            p_opp_0[i] = 0; p_my_0[i] = 0;
            for (j=0;j<3;j++) {
                p_opp_1[i][j] = 0; p_my_1[i][j] = 0;
                for (k=0;k<3;k++) {
                    p_opp_2[i][j][k] = 0; p_my_2[i][j][k] = 0;
                    p_oppmy_2[i][j][k] = 0; p_myopp_2[i][j][k] = 0;
                    for (m=0;m<3;m++) {
                        p_opp_3[i][j][k][m] = 0; p_my_3[i][j][k][m] = 0;
                    }
                }
            }
        }
        return( adRAND_INT(3));
    }

    if (last_pred == oL) wins++;

    noise = (float)(wins/ng);

    /* TABULATE OVERALL FEQUENCY OF ACTIONS */
    p_opp_0[oL]++;
    p_my_0[mL]++;

    r = p_opp_0[rock]; p = p_opp_0[paper]; s = p_opp_0[scissors];

    /* GET FREQUENCIES OF ACTIONS FOLLOWING OUR LAST MOVES */
    if (ng > 1) { /* adDEPTH == 1 */
        ++p_opp_1[oL][oL1];
        ++p_my_1[oL][mL1];
        r += p_opp_1[rock][oL] + p_my_1[rock][mL];
        p += p_opp_1[paper][oL] + p_my_1[paper][mL];
        s += p_opp_1[scissors][oL] + p_my_1[scissors][mL];
                
        if (ng > 2 && adDEPTH >= 2) { /* adDEPTH == 2 */
            ++p_opp_2[oL][oL1][oL2];
            ++p_my_2[oL][mL1][mL2];
            ++p_oppmy_2[oL][oL1][mL2];
            ++p_myopp_2[oL][mL1][oL2];
        
            r += p_opp_2[rock][oL][oL1] + p_my_2[rock][mL][mL1] + p_oppmy_2[rock][oL][mL1] + p_myopp_2[rock][mL][oL1];
            p += p_opp_2[paper][oL][oL1] + p_my_2[paper][mL][mL1] + p_oppmy_2[paper][oL][mL1] + p_myopp_2[paper][mL][oL1];
            s += p_opp_2[scissors][oL][oL1] + p_my_2[scissors][mL][mL1] + p_oppmy_2[scissors][oL][mL1] + p_myopp_2[scissors][mL][oL1];
            
            if (ng > 3 && adDEPTH >= 3) { /* adDEPTH == 3 */
                ++p_opp_3[oL][oL1][oL2][oL3];
                ++p_my_3[oL][mL1][mL2][mL3];

                r += p_opp_3[rock][oL][oL1][oL2] + p_my_3[rock][mL][mL1][mL2];
                p += p_opp_3[paper][oL][oL1][oL2] + p_my_3[paper][mL][mL1][mL2];
                s += p_opp_3[scissors][oL][oL1][oL2] + p_my_3[scissors][mL][mL1][mL2];
            }
        }
    } 

    pR = r/(float)(r+p+s);
    pP = p/(float)(r+p+s);
    pS = s/(float)(r+p+s);

    if (pR > pP && pR > pS) { /* predict rock */
        last_pred = rock;
        if (flip_biased_coin(noise*pS)) return rock;
        else if (flip_biased_coin(noise*pP)) return scissors;
        else return paper;
    } else if (pP > pR && pP > pS) { /* predict paper */
        last_pred = paper;
        if (flip_biased_coin(noise*pS)) return rock;
        else if (flip_biased_coin(noise*pR)) return paper;
        else return scissors;
    } else if (pS > pP && pS > pR) { /* predict scissors */
        last_pred = scissors;
        if (flip_biased_coin(noise*pR)) return paper;
        else if (flip_biased_coin(noise*pP)) return scissors;
        else return rock;
    } else if (pR == pS && pR == pP) {
        last_pred = -1;
        return(adRAND_INT(3));
    } else if (pR == pP) {
        last_pred = biased_roshambo(0.5,0.5);
        if (flip_biased_coin(noise*pS)) return rock;
        return last_pred;
    } else if (pR == pS) {
        last_pred = biased_roshambo(0.5,0.0);
        if (flip_biased_coin(noise*pP)) return scissors;
        return last_pred;
    } else if (pS == pP) {
        last_pred = biased_roshambo(0.0,0.5);
        if (flip_biased_coin(noise*pR)) return paper;
        return last_pred;
    }
    last_pred = -1;
    return (adRAND_INT(3));
}
/**********************************************************************/


/*  Entrant:  ZQ Bot (22)   Neil Burch (Can)  */

#define ZQ_MAXR 2147483645
#define ZQ_TIE 0
#define ZQ_WIN 1
#define ZQ_LOSS 2
#define ZQ_MOVE_PAIR( me, them ) (me)*3+(them)
#define ZQ_MAX_NODES 65536
#define ZQ_MAX_LOSS 15

typedef struct ZQ_NODE
{
  struct ZQ_NODE *children;
  int count;
} zq_node_t;

static zq_node_t zq_root_node, *zq_root = NULL;
static int zq_num_nodeblocks, zq_patt_length = 9;

static int zq_calc_result( int me, int them )
{
  int t;

  t = ( me - them ) % 3;
  if( t < 0 )
    t += 3;
  return t;
}

static zq_node_t *zq_new_nodeblock()
{
  int i;
  zq_node_t *t;

  if( zq_num_nodeblocks >= ZQ_MAX_NODES )
    return NULL;
  zq_num_nodeblocks++;
  t = malloc( sizeof( zq_node_t ) * 9 );
  if( !t )
    return NULL;
  for( i = 0; i < 9; i++ ) {
    t[ i ].children = NULL;
    t[ i ].count = 0;
  }
  return t;
}

static int zq_random_move()
{
  /* random%3 does not produce an equal distribution */
  int t;

  do {
    t = random();
  } while( t > ZQ_MAXR );
  return t % 3;
}

static void zq_kill_children( zq_node_t *node )
{
  int i;

  if( !node->children )
    return;
  for( i = 0; i < 9; i++ )
    zq_kill_children( &( node->children[ i ] ) );
  free( node->children );
}

static int zq_init()
{
  int i;

  if( zq_root )
    zq_kill_children( zq_root );

  zq_root = &zq_root_node;
  zq_num_nodeblocks = 0;

  /* ensure at least two moves can be remembered */
  if( !( zq_root_node.children = zq_new_nodeblock() ) ) {
    fprintf( stderr, "Give me a break! Not enough memory for 72 bytes?\n" );
    return -1;
  }
  for( i = 0; i < 9; i++ )
    if( !( zq_root->children[ i ].children = zq_new_nodeblock() ) )
      return -1;
  return 0;
}

static void zq_walk_history()
{
  int start, i;
  zq_node_t *node;

  if( !my_history[ 0 ] )
    return;

  /* walk the tree for last zq_patt_length moves, last 6, ..., last move */
  start = my_history[ 0 ] - zq_patt_length + 1;
  if( start < 1 )
    start = 1;
  for( ; start <= my_history[ 0 ]; start++ ) {
    node = zq_root;
    for( i = start; i <= my_history[ 0 ]; i++ ) {
      if( !node->children )
        if( !( node->children = zq_new_nodeblock() ) )
          break;
      node = &( node->children[ ZQ_MOVE_PAIR( my_history[ i ],
                                           opp_history[ i ] ) ] );
    }
    if( i > my_history[ 0 ] )
      node->count++;
  }
}

int zq_move()
{
  static char losestreak;
  int start, i, j, counts[ 3 ], move, closs;
  zq_node_t *node;

  move = 0; closs = 0; /* -db */
  if( !my_history[ 0 ] ) {
    losestreak = 0;
    closs = 0;
    zq_init();
  }

  if( zq_calc_result( my_history[ my_history[ 0 ] ],
                      opp_history[ my_history[ 0 ] ] ) == ZQ_LOSS ) {
    if( losestreak ) {
      closs++;
      if( closs == ZQ_MAX_LOSS ) {
        losestreak = 0;
        closs = 0;
        zq_init();
      }
    } else {
      losestreak = 1;
      closs = 1;
    }
  } else
    losestreak = 0;

  /* update tree */
  zq_walk_history();

  for( i = 0; i < 3; i++ )
    counts[ i ] = 0;
  start = my_history[ 0 ] - zq_patt_length + 1;
  if( start < 1 )
    start = 1;
  for( ; start <= my_history[ 0 ]; start++ ) {
    node = zq_root;
    for( i = start; i <= my_history[ 0 ]; i++ ) {
      if( !node->children )
        break;
      node = &( node->children[ ZQ_MOVE_PAIR( my_history[ i ],
                                           opp_history[ i ] ) ] );
    }
    if( i > my_history[ 0 ] )
      if( node->children )
        for( i = 0; i < 3; i++ ) /* opponent choice */
          for( j = 0; j < 3; j++ ) /* my choice */
            counts[ i ] += node->children[ ZQ_MOVE_PAIR( j, i ) ].count *
              node->count;
  }

  if( counts[ 1 ] > counts[ 0 ] )
    j = counts[ 1 ];
  else
    j = counts[ 0 ];
  if( counts[ 2 ] > j )
    j = counts[ 2 ];

  i = 0;
  if( counts[ 0 ] == j )
    i++;
  if( counts[ 1 ] == j )
    i++;
  if( counts[ 2 ] == j )
    i++;

  if( i == 3 )
    move = zq_random_move();
  else if( ( i == 1 ) || ( random() & 1 ) ) {
    /* only one choice, or first choice of two */
    for( i = 0; i < 3; i++ )
      if( counts[ i ] == j ) {
move = i;
        break;
      }
  } else {
    for( i = 2; i >= 0; i-- )
      if( counts[ i ] == j ) {
        move = i;
        break;
      }
  }

  return ( move + 1 ) % 3;
}
/* ---------- Neil's code ends here ---------- */
/**********************************************************************/


/*  Entrant:  Sweet Rocky (24)   Lourdes Pena (Mex)  */

/*********** Lourdes Pena Castillo September, 1999 ***************/
/*********** Sweet Rocky program                    **************/
#define LMIN2 2
#define LBAD -40
#define LTH .80

int sweetrock ()
{
   /* play whatever will beat the opponent's most frequent choice after 
    previous match history */

    static int count[3][3][3]; /*[Idid][Itdid][Itdoes];*/
    static int lastTime[3][3][1]; /*[Idid][Itdid][Itdid] */
    static int score, goingbad;
    int *pCount, *pLast, total, choice, pred;
    float diff;

    if ( my_history[0] == 0 ) {
       memset(count, 0, sizeof(int)*27);
       memset(lastTime, 0, sizeof(int)*9);
       score = 0; 
       goingbad = 0; 
       return ( biased_roshambo(0.33, 0.33) ); /* Be optimal first */
    }

    if ( my_history[0] < LMIN2 ) {
       if ((opp_history[opp_history[0]] - my_history[my_history[0]] == 1) || 
          (opp_history[opp_history[0]] - my_history[my_history[0]] == -2)) {
          score --;
       } else if (opp_history[opp_history[0]] != my_history[my_history[0]]) {
          score ++;
       }
       return ( biased_roshambo(0.33, 0.33) ); /* Be optimal first */
    } 

    /* Add the previous result information */
    pCount = count[my_history[my_history[0]-1]][opp_history[opp_history[0]-1]];
    pCount[opp_history[opp_history[0]]]++; 

    if ( opp_history[opp_history[0]] - my_history[my_history[0]] == 1 || 
       opp_history[opp_history[0]] - my_history[my_history[0]] == -2) {
       score --;
    } else if (opp_history[opp_history[0]] != my_history[my_history[0]]) {
       score ++;
    }

    if (score == LBAD ) goingbad = 1; 

    if ( goingbad ) { /* oh-oh! Things are going bad! */
       return ( biased_roshambo(0.333, 0.333) ); /* better be optimal then */
    }
       
    pLast = lastTime[my_history[my_history[0]-1]][opp_history[opp_history[0]-1]];
    pLast[0] = opp_history[opp_history[0]];

    /* Look what the numbers say the opponent will do next */
    pCount = count[my_history[my_history[0]]][opp_history[opp_history[0]]];
    total = pCount[rock] + pCount[paper] + pCount[scissors];

    if (total == 0 ){ /*Not information, then be optimal */
      return ( biased_roshambo(0.33, 0.33) ); 
    }

    /* What the opp. did last time */
    pLast = lastTime[my_history[my_history[0]]][opp_history[opp_history[0]]];

    if ( (pCount[rock] > pCount[paper]) && (pCount[rock] > pCount[scissors]) ) {
       pred = rock;
       choice = paper; 
    } else if ( pCount[paper] > pCount[scissors] ) { 
       pred = paper;
       choice = scissors; 
    } else { 
       pred = scissors;
       choice = rock; 
    }

    /* Maybe the choice is close! */
    if (pred != pLast[0]  ) { 
       diff = (float) pCount[pLast[0]] / (float) pCount[pred];  
       if ( diff > LTH ) {
         if (flip_biased_coin(1 - diff)){
             return (pLast[0]);
         } else {
             return (choice);
         }
       } 
    }   
    return (choice);
}
/**********************************************************************/


/*  Entrant:  Piedra (25)   Lourdes Pena (Mex)  */

/*********** Lourdes Pena Castillo September, 1999 ***************/
/*********** Piedra  program                        **************/
#define LMIN1 2
#define LBAD -40

int piedra ()
{
   /* play whatever will beat the opponent's most frequent choice
      after previous match history */

    static int Count[3][3][3]; /*[Idid][Itdid][Itdoes];*/
    static int score, goingbad;
    int *pCount, total;

    if ( my_history[0] == 0 ) {
       memset(Count, 0, sizeof(int)*27);
       score = 0; 
       goingbad = 0; 
       return ( biased_roshambo(0.33, 0.33) ); /* Be optimal first */
    }

    if ( my_history[0] < LMIN1 ) {
       if ((opp_history[opp_history[0]] - my_history[my_history[0]] == 1) || 
          (opp_history[opp_history[0]] - my_history[my_history[0]] == -2)) {
          score --;
       } else if (opp_history[opp_history[0]] != my_history[my_history[0]]) {
          score ++;
       }
       return ( biased_roshambo(0.33, 0.33) ); /* Be optimal first */
    } 

    /* Add the previous result information */
    pCount = Count[my_history[my_history[0]-1]][opp_history[opp_history[0]-1]];
    pCount[opp_history[opp_history[0]]]++; 
       

    if ( opp_history[opp_history[0]] - my_history[my_history[0]] == 1 || 
       opp_history[opp_history[0]] - my_history[my_history[0]] == -2) {
       score --;
    } else if (opp_history[opp_history[0]] != my_history[my_history[0]]) {
       score ++;
    }

    if (score == LBAD ) goingbad = 1; 

    if ( goingbad ) { /* oh-oh! Things are going bad! */
       return ( biased_roshambo(0.333, 0.333) ); /* better be optimal then */
    }

    /* Look what the numbers say the opponent will do next */
    pCount = Count[my_history[my_history[0]]][opp_history[opp_history[0]]];
    total = pCount[rock] + pCount[paper] + pCount[scissors];

    if (total == 0 ){ /*Not information, then be optimal */
       return ( biased_roshambo(0.33, 0.33) ); 
    }

    if ( (pCount[rock] > pCount[paper]) && (pCount[rock] > pCount[scissors]) ) {
      return( paper); 
    } else if ( pCount[paper] > pCount[scissors] ) { 
      return( scissors); 
    } else { 
      return ( rock ); 
    }
}
/**********************************************************************/


/*  Entrant:  Mixed Strategy (28)   Thad Frogley (UK)

   > I also welcome more feedback from the participants, both
   > on your ideas and on your personal background. 

 Darse,
 
 As I said in an earlier mail I thought it was a very well run tournament,
 and I will be entering the second one, probably with an cleaner/faster
 "mixed strategy" bot, plus a new one that's been busting my brain since I
 read about "Iocaine Powder" (so do I play what will beat what I predict they
 will play, or do I play what will beat what will beat what I predict that
 they predict what I will play?  Ungk.  Fizzle.).
 
 Anywho, ask you asked, my info:
 
 I am:
 Thad (Thaddaeus Frogley) 24 years old, programmer for CLabs/CyberLife
 Technology Ltd, Cambridge, England
 No university education, self taught programmer (from ooh around the age of
 7 hmmm zx81 with 16k ram pack!).
 Maintainer (but not very active) of the Robot Battle FAQ
 [http://www.robotbattle.com]
 Oh, and some people seem to find it interesting that I'm dyslexic.
 
 My bot is:
 Mixed Strategy, and is *not* based on the CLabs alife philosophy, it is
 instead based on my experiences with Robot Battle (RB) where the Muli-mode
 Bot / Mode Switcher / Meta Bot is a well established tactic.
 
 Initially I thought that simply wrapping the built in behaviours in a basic
 analysing mode switcher would be enough to do well in the tournament (I
 seriously under estimated the calibre of the participants), but then after
 brief correspondence with your good self I got that nagging feeling that I
 needed to do more.  Due to time constraints I limited my changes to the
 creation of two 'new' behaviours based on pair wise statistical probability
 predication (named watching-you and watching-you-watching-me) and stripped
 out the modes that I felt where redundant.  In hindsight I have realised
 that I could have probably removed the "Beat Frequent Pick" and "random"
 modes leaving the random factor to the context switching between the
 remaining modes.
 
 I have some other ideas for improving Mixed Strategy, and I have an idea for
 a new bot, but I'll save them for next time.
 
 I'll close by pointing out the following issues common to all mode based
 adaptive AIs.
 
 1) The learning curve.  To many modes means to much time spend learning, and
 not enough winning.
 2) Mode locking.  Without a decay function a mode that is adapted against
 will loose as many as it won before switching.  (Hence the decay function in
 my one.)
 
 I hope this lot adds to everybody's knowledge and enjoyment of the game!
 
 Thad
*/

int mixed_strategy()
{
  static int strategy_scores[4];
  static int last_strategy;
  int i, rcount, pcount, scount;

  int turn = opp_history[0];
  double t;

  if( turn == 0 ) {
    strategy_scores[0] = 4;     /* watching you watching me */
    strategy_scores[1] = 4;     /* watching you  */
    strategy_scores[2] = 2;     /* freqbot */
    strategy_scores[3] = 1;     /* random */
  }
  else{
    /* remeber success of prev stratigies */
    if (my_history[turn] == opp_history[turn]){
      strategy_scores[last_strategy] += 1;  /* draw */
    }
    else if ( (my_history[turn]-opp_history[turn] == 1) || 
              (my_history[turn]-opp_history[turn] == -2) ) {
      strategy_scores[last_strategy] += 3;  /* win (test from Play_Match) */
    }
    else{
      strategy_scores[last_strategy] =
        (int)((double)strategy_scores[last_strategy]*0.8);
    }
  }

  /* pick based on rate of success for each strategy */
  t = random();
  t /= maxrandom;
  t *= (strategy_scores[0] + strategy_scores[1] + strategy_scores[2] +
        strategy_scores[3]);

  if (t<strategy_scores[0]){
    last_strategy = 0;
    /* play whatever will beat the opponent's most frequent follow up to
       my last move */

    rcount = 0;  pcount = 0;  scount = 0;
    for (i = 2; i <= opp_history[0]-1; i++) {
      if (my_history[i-1]==my_history[opp_history[0]]){
        if (opp_history[i] == rock)            { rcount++; }
        else if (opp_history[i] == paper)      { pcount++; }
        else /* opp_history[i] == scissors */  { scount++; }
      }
    }
    if ( (rcount > pcount) && (rcount > scount) ) { return(paper); }
    else if ( pcount > scount ) { return(scissors); }
    else { return(rock); }
  }
  else if (t<strategy_scores[0]+strategy_scores[1]){ /* note change */
    last_strategy = 1;
    /* play whatever will beat the opponent's most frequent follow up to his
       last move */

    rcount = 0;  pcount = 0;  scount = 0;
    for (i = 2; i <= opp_history[0]-1; i++) {
      if (opp_history[i-1]==opp_history[opp_history[0]]){
        if (opp_history[i] == rock)            { rcount++; }
        else if (opp_history[i] == paper)      { pcount++; }
        else /* opp_history[i] == scissors */  { scount++; }
      }
    }
    if ( (rcount > pcount) && (rcount > scount) ) { return(paper); }
    else if ( pcount > scount ) { return(scissors); }
    else { return(rock); }
    
  }
  else if (t<strategy_scores[0]+strategy_scores[1]+strategy_scores[2]){
    last_strategy = 2;
    /* play whatever will beat the opponent's most frequent choice */

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
  else{
    last_strategy = 3;
    return( random() % 3);
  } 
}
/**********************************************************************/


/*  Entrant:  Multi-strategy (38)   Mark James (Can) */

typedef struct RollingAverage
{
  float total;
  int count;
  int size;
  int next;
  float* data;
} RollingAverage;

RollingAverage* RollingAverage_new(int size);
void RollingAverage_delete(RollingAverage* avg);
float RollingAverage_Add(RollingAverage* avg, float element);
float RollingAverage_Average(RollingAverage* avg);

typedef struct Strategy {
  RollingAverage* success;
  int(*function)();
  int lastmove;
  int used;
} Strategy;

extern Strategy* Strategy_new(int(*function)(), int length);
extern void      Strategy_delete(Strategy* stgy);
void             Strategy_Use(Strategy* stgy);
int              Strategy_Used(Strategy* stgy);

extern void MD5Init();
extern unsigned int MD5Random();

#define strategy_count 7
#define AVGLEN 50

extern int opp_history[];
extern int my_history[];

Strategy** strategies = NULL;

int
FirstTrial()
{
  return opp_history[0] == 0;
}

static int
random_md5()
{
  if(FirstTrial())
  {
    MD5Init();
  }
  return MD5Random() % 3;
}

static int
mrockbot ()
{
  /* "Good ole rock.  Nuthin' beats rock." */
  return(rock);
}

static int
mpaperbot ()
{
  return(paper);
}

static int
mscissorsbot ()
{
  return(scissors);
}

static int
beatcopybot()
{
    return( (my_history[my_history[0]] + 2) % 3);
}

int
beatswitchbot ()
{
  /* assume opponent never repeats the previous pick */
  if ( opp_history[opp_history[0]] == rock )
  {
    return(scissors);
  }
  else if ( opp_history[opp_history[0]] == paper )
  {
    return( rock );
  }
  else return( paper );
}

int beatfreqbot ()
{
    /* play whatever will beat the freqbot choice */

    int i, rcount, pcount, scount;

    rcount = 0;  pcount = 0;  scount = 0;
    for (i = 1; i <= my_history[0]; i++) {
        if (my_history[i] == rock)            { rcount++; }
        else if (my_history[i] == paper)      { pcount++; }
        else /* my_history[i] == scissors */  { scount++; }
    }
    if ( (rcount > pcount) && (rcount > scount) ) { return(scissors); }
    else if ( pcount > scount ) { return(rock); }
    else { return(paper); }
}

int
Strategy_Move(Strategy* stgy)
{
  int move = (stgy->function)();
  stgy->lastmove = move;
  return move;
}

void
Strategy_Use(Strategy* stgy)
{
  stgy->used++;
}

int
Strategy_Used(Strategy* stgy)
{
  return stgy->used;
}

float
Score(int round, int move)
{
  int p1 = move;
  int p2 = opp_history[round];

  if (p1 == p2) {
    return 0.5f;
  }
  else if ( (p1-p2 == 1) || (p1-p2 == -2) ) {
    return 1.0f;
  }
  else if ( (p2-p1 == 1) || (p2-p1 == -2) ) {
    return 0.0f;
  }
  else printf("Error: should not be reached.\n");
  return 0.0f;
}

int multibot()
{
  int i;

  if(FirstTrial())
  {
    /* New round */
    if(strategies)
    {
      for( i = 0; i < strategy_count; i++)
      {
        Strategy_delete(strategies[i]);
      }
      free(strategies);
      strategies = NULL;
    }
    strategies = (Strategy**) malloc(sizeof(Strategy*) * strategy_count);

    strategies[0] = Strategy_new(random_md5,AVGLEN);
    strategies[1] = Strategy_new(mrockbot,AVGLEN);
    strategies[2] = Strategy_new(mpaperbot,AVGLEN);
    strategies[3] = Strategy_new(mscissorsbot,AVGLEN);
    strategies[4] = Strategy_new(beatcopybot,AVGLEN);
    strategies[5] = Strategy_new(beatswitchbot,AVGLEN);
    strategies[6] = Strategy_new(beatfreqbot,AVGLEN);

    return random_md5();
  } else {
    /* update sucesses and find best */
    float best = 0.0f;
    int beststrategy = 0;
    int bestmove = 0;
    for( i = 0; i < strategy_count ; i++)
    {
      float success = RollingAverage_Add(strategies[i]->success,
                                         Score(opp_history[0], strategies[i]->lastmove));
      int move = Strategy_Move(strategies[i]);

      if(success > best)
      {
        best = success;
        beststrategy = i;
        bestmove = move;
      }
    }

    /* play the best move */
    return bestmove;
  }
}

RollingAverage*
RollingAverage_new(int size)
{
  int i;
  RollingAverage* avg = (RollingAverage*) malloc(sizeof(RollingAverage));
  avg->total = 0.0f;
  avg->count = 0;
  avg->next = 0;
  avg->size = size;
  avg->data = (float*) malloc(sizeof(float) * size);
  for( i = 0 ; i < size ; i++)
  {
    avg->data[i] = 0.0f;
  }
  return avg;
}

void
RollingAverage_delete(RollingAverage* avg)
{
  free(avg->data);
  free(avg);
}

float
RollingAverage_Add(RollingAverage* avg, float element)
{
  avg->total -= avg->data[avg->next];
  avg->data[avg->next] = element;
  avg->next = (avg->next + 1) % avg->size;
  avg->total += element;
  avg->count++;
  if(avg->count > avg->size)
  {
    avg->count = avg->size;
  }
  return RollingAverage_Average(avg);
}

float
RollingAverage_Average(RollingAverage* avg)
{
  if(avg->count == 0)
  {
    return 0.0f;
  } else {
    /*
    printf("Total: %f Count: %d Avg: %f\n",
           avg->total,
           avg->count,
           avg->total / avg->count); */

    return avg->total / avg->count;
  }
}

Strategy*
Strategy_new(int(*function)(), int length)
{
  Strategy* result = (Strategy*) malloc(sizeof(Strategy));
  result->success = RollingAverage_new(length);
  result->function = function;
  result->lastmove = 0;
  result->used = 0;
  return result;
}

void
Strategy_delete(Strategy* stgy)
{
  RollingAverage_delete(stgy->success);
  free(stgy);
}

/*
 * MD5 transform algorithm, taken from code written by Colin Plumb,
 * and put into the public domain
 */

/* The four core functions */

#define F1(x, y, z) (z ^ (x & (y ^ z)))
#define F2(x, y, z) F1(z, x, y)
#define F3(x, y, z) (x ^ y ^ z)
#define F4(x, y, z) (y ^ (x | ~z))

/* This is the central step in the MD5 algorithm. */
#define MD5STEP(f, w, x, y, z, data, s) ( w += f(x, y, z) + data,  w = w<<s | w>>(32-s),  w += x )

/*
 * The core of the MD5 algorithm, this alters an existing MD5 hash to
 * reflect the addition of 16 longwords of new data.  MD5Update blocks
 * the data and converts bytes into longwords for this routine.
 */
static void MD5Transform(unsigned int buf[4],
                         unsigned int const in[16])
{
  unsigned int a, b, c, d;

  a = buf[0];
  b = buf[1];
  c = buf[2];
  d = buf[3];

  MD5STEP(F1, a, b, c, d, in[ 0]+0xd76aa478,  7);
  MD5STEP(F1, d, a, b, c, in[ 1]+0xe8c7b756, 12);
  MD5STEP(F1, c, d, a, b, in[ 2]+0x242070db, 17);
  MD5STEP(F1, b, c, d, a, in[ 3]+0xc1bdceee, 22);
  MD5STEP(F1, a, b, c, d, in[ 4]+0xf57c0faf,  7);
  MD5STEP(F1, d, a, b, c, in[ 5]+0x4787c62a, 12);
  MD5STEP(F1, c, d, a, b, in[ 6]+0xa8304613, 17);
  MD5STEP(F1, b, c, d, a, in[ 7]+0xfd469501, 22);
  MD5STEP(F1, a, b, c, d, in[ 8]+0x698098d8,  7);
  MD5STEP(F1, d, a, b, c, in[ 9]+0x8b44f7af, 12);
  MD5STEP(F1, c, d, a, b, in[10]+0xffff5bb1, 17);
  MD5STEP(F1, b, c, d, a, in[11]+0x895cd7be, 22);
  MD5STEP(F1, a, b, c, d, in[12]+0x6b901122,  7);
  MD5STEP(F1, d, a, b, c, in[13]+0xfd987193, 12);
  MD5STEP(F1, c, d, a, b, in[14]+0xa679438e, 17);
  MD5STEP(F1, b, c, d, a, in[15]+0x49b40821, 22);

  MD5STEP(F2, a, b, c, d, in[ 1]+0xf61e2562,  5);
  MD5STEP(F2, d, a, b, c, in[ 6]+0xc040b340,  9);
  MD5STEP(F2, c, d, a, b, in[11]+0x265e5a51, 14);
  MD5STEP(F2, b, c, d, a, in[ 0]+0xe9b6c7aa, 20);
  MD5STEP(F2, a, b, c, d, in[ 5]+0xd62f105d,  5);
  MD5STEP(F2, d, a, b, c, in[10]+0x02441453,  9);
  MD5STEP(F2, c, d, a, b, in[15]+0xd8a1e681, 14);
  MD5STEP(F2, b, c, d, a, in[ 4]+0xe7d3fbc8, 20);
  MD5STEP(F2, a, b, c, d, in[ 9]+0x21e1cde6,  5);
  MD5STEP(F2, d, a, b, c, in[14]+0xc33707d6,  9);
  MD5STEP(F2, c, d, a, b, in[ 3]+0xf4d50d87, 14);
  MD5STEP(F2, b, c, d, a, in[ 8]+0x455a14ed, 20);
  MD5STEP(F2, a, b, c, d, in[13]+0xa9e3e905,  5);
  MD5STEP(F2, d, a, b, c, in[ 2]+0xfcefa3f8,  9);
  MD5STEP(F2, c, d, a, b, in[ 7]+0x676f02d9, 14);
  MD5STEP(F2, b, c, d, a, in[12]+0x8d2a4c8a, 20);

  MD5STEP(F3, a, b, c, d, in[ 5]+0xfffa3942,  4);
  MD5STEP(F3, d, a, b, c, in[ 8]+0x8771f681, 11);
  MD5STEP(F3, c, d, a, b, in[11]+0x6d9d6122, 16);
  MD5STEP(F3, b, c, d, a, in[14]+0xfde5380c, 23);
  MD5STEP(F3, a, b, c, d, in[ 1]+0xa4beea44,  4);
  MD5STEP(F3, d, a, b, c, in[ 4]+0x4bdecfa9, 11);
  MD5STEP(F3, c, d, a, b, in[ 7]+0xf6bb4b60, 16);
  MD5STEP(F3, b, c, d, a, in[10]+0xbebfbc70, 23);
  MD5STEP(F3, a, b, c, d, in[13]+0x289b7ec6,  4);
  MD5STEP(F3, d, a, b, c, in[ 0]+0xeaa127fa, 11);
  MD5STEP(F3, c, d, a, b, in[ 3]+0xd4ef3085, 16);
  MD5STEP(F3, b, c, d, a, in[ 6]+0x04881d05, 23);
  MD5STEP(F3, a, b, c, d, in[ 9]+0xd9d4d039,  4);
  MD5STEP(F3, d, a, b, c, in[12]+0xe6db99e5, 11);
  MD5STEP(F3, c, d, a, b, in[15]+0x1fa27cf8, 16);
  MD5STEP(F3, b, c, d, a, in[ 2]+0xc4ac5665, 23);

  MD5STEP(F4, a, b, c, d, in[ 0]+0xf4292244,  6);
  MD5STEP(F4, d, a, b, c, in[ 7]+0x432aff97, 10);
  MD5STEP(F4, c, d, a, b, in[14]+0xab9423a7, 15);
  MD5STEP(F4, b, c, d, a, in[ 5]+0xfc93a039, 21);
  MD5STEP(F4, a, b, c, d, in[12]+0x655b59c3,  6);
  MD5STEP(F4, d, a, b, c, in[ 3]+0x8f0ccc92, 10);
  MD5STEP(F4, c, d, a, b, in[10]+0xffeff47d, 15);
  MD5STEP(F4, b, c, d, a, in[ 1]+0x85845dd1, 21);
  MD5STEP(F4, a, b, c, d, in[ 8]+0x6fa87e4f,  6);
  MD5STEP(F4, d, a, b, c, in[15]+0xfe2ce6e0, 10);
  MD5STEP(F4, c, d, a, b, in[ 6]+0xa3014314, 15);
  MD5STEP(F4, b, c, d, a, in[13]+0x4e0811a1, 21);
  MD5STEP(F4, a, b, c, d, in[ 4]+0xf7537e82,  6);
  MD5STEP(F4, d, a, b, c, in[11]+0xbd3af235, 10);
  MD5STEP(F4, c, d, a, b, in[ 2]+0x2ad7d2bb, 15);
  MD5STEP(F4, b, c, d, a, in[ 9]+0xeb86d391, 21);

  buf[0] += a;
  buf[1] += b;
  buf[2] += c;
  buf[3] += d;
}

#undef F1
#undef F2
#undef F3
#undef F4
#undef MD5STEP


unsigned int MD5Buf[4];
unsigned int MD5In[16];

int MD5BufInit [] =
{
  0x67452301,
  0xefcdab89,
  0x98badcfe,
  0x10325476
};

void
MD5Init()
{
  int i;
  for(i = 0; i < 4; i++)
  {
    MD5Buf[i] = MD5BufInit[i];
  }

  for(i = 0; i < 16; i++)
  {
    MD5In[i] = MD5Buf[i % 4] + MD5Buf[i / 4];
  }
}

unsigned int
MD5Random()
{
  int i;
  MD5Transform ( MD5Buf, MD5In );
  for(i = 0; i < 16; i++)
  {
    MD5In[i] = MD5Buf[i % 4] + MD5Buf[i / 4];
  }

  return MD5Buf[0];
}

int asterious()  /* Kastellanos Nikos (36 lines) */
{
 /* ASTERIOUS v1.01 */
 /* Program by Kastellanos Nikos  */
 /* datacrime@freemail.gr   */

 int res;
 int trial=0;

 int static base=0;
 int static weirdo=1;

 /*  Get a random result */
 res=random()%3;

 /*  Handle base and weirdo */
 trial=my_history[0];
 if(trial>0  &&  my_history[trial]==rock      &&  opp_history[trial]==paper)
   base+=2;
 if(trial>0  &&  my_history[trial]==paper     &&
    opp_history[trial]==scissors) base+=2;
 if(trial>0  &&  my_history[trial]==scissors  &&  opp_history[trial]==rock)
   base+=2;
 if(trial>0  &&  my_history[trial]==opp_history[trial])     base+=1;
 if(base<0) base=0;
 if(base>9) {base=0;weirdo=(weirdo+1%3);} /*  6,9,12,15 are good BASE numbers. */

 /*  do the AI stuff... */
 if(trial>0) res=opp_history[trial];

 /*  Schisophrenic Behavior. */
 res=res+weirdo;

 return( res%3 );
}
/**********************************************************************/


/*  Entrant:  Peterbot (50)   Peter Baylie (USA)  */

int peterbot()
{
    /* maintain stats with static variables to avoid re-scanning the
       history array */
    static struct tri { int r, p, s; } oc, mc;
    int opp_last, opp_prev, my_last, my_prev, myfreq, i;

    opp_prev = 0; my_prev = 0; /* -db */
    if( opp_history[0] == 0 ) {
        oc.r = 0;  oc.p = 0;  oc.s = 0;  
        opp_last = random()%3;
        opp_prev = random()%3;
    }
    else {
      opp_last = opp_history[opp_history[0]];
      if (opp_history[0]!=1) opp_prev = opp_history[opp_history[0]-1];
      if ( opp_last == rock)          { oc.r++; }
      else if ( opp_last == paper)    { oc.p++; }
      else                            { oc.s++; }
    }

    if( my_history[0] == 0 ) {
        mc.r = 0;  mc.p = 0;  mc.s = 0;  
        my_last = random()%3;
        my_prev = random()%3;
    }
    else {
      my_last = my_history[my_history[0]];
      if (my_history[0]!=1) my_prev = my_history[my_history[0]-1];
      if ( my_last == rock)          { mc.r++; }
      else if ( my_last == paper)    { mc.p++; }
      else                           { mc.s++; }
    }

/* beat stupid */
    if ( (oc.r - oc.p - oc.s) > 0 ) { return(paper); }
    else if ( (oc.p - oc.r - oc.s) > 0 ) { return(scissors); }
    else if ( (oc.s - oc.p - oc.r) > 0) { return(rock); }
  
/* beat rotate */
    i = opp_history[0]-50;
    if (i<0) i=1;
    while ((i<opp_history[0]) && ((opp_history[i]+1)%3==opp_history[i+1]))
           i++;
    if (i==opp_history[0]) {
       return ((opp_history[i]+2)%3); 
};

/* beat freq */
if ( (mc.r > mc.p) && (mc.r > mc.s) ) myfreq = paper;
   else if ( mc.p > mc.s ) myfreq = scissors;
        else myfreq = rock;
if (myfreq == opp_last && myfreq == opp_prev) { 
   return (opp_last+1)%3;
};

/* beat switching */
    if (opp_last!=opp_prev) {
       i = 0;
       while ((i==opp_last) || (i==opp_prev)) i++;
       return (i+1)%3;
    };

    /* beat last */
if (opp_last == (my_prev+1)%3) {
   return (my_last+2)%3;
};

/* be random */
    return random() % 3;
}
/**********************************************************************/


/*  Entrant:  Inocencio (44)   Rafael Morales (Mex)

 Darse,
 
 Thank you very much for your email about the results from the 
 competition. They are extremely interesting and revealing. Certainly, 
 I never thought the competition were a waste of time, but a clearly 
 underestimate the richness of possible (good) solutions available. 
 The range of techniques discussed in your email gives me a clearer 
 idea of the complexity of opponent modelling. (My own research is on 
 learner modelling, but since I am interested in learning to play 
 games as test-bed application I should know better about opponent 
 modelling).
 
 Inocencio's results were pretty bad, as it deserved.  No surprise 
 after reading the descriptions of the strongest players.  I am 
 looking forward to hearing about the next competition.  If I decided 
 to participate, I shall do a much better job.
 
 Congratulations.  You have done a very good job.
 
 ==
 Rafael Morales (PhD student)                | 80 South Bridge
 School of Artificial Intelligence           | Edinburgh
 Division of Informatics                     | EH1 1HN
 University of Edinburgh                     | Scotland, UK
 
*/
int inocencio ()  /* based on freqbot2 code */
{
    static int rcount, pcount, scount;

    int opp_last;
    int opp_fgt;
    int n, total;

    float rstat, pstat, sstat;

    float pat[27][3];
    float mypat[27][3];
    int patCount[27];
    int mypatCount[27];
    float probs[3], my_probs[3];
    int i, j, b, pi, x;

    pi = 0; /* -db */
    n = opp_history[0];

    if ( n == 0 ) {
      rcount = 0;  pcount = 0;  scount = 0;
    } else {
      opp_last = opp_history[n];
      if ( opp_last == rock)          { rcount++; }
      else if ( opp_last == paper)    { pcount++; }
      else /* opp_last == scissors */ { scount++; }
      
      if (n > 20) {
        opp_fgt = opp_history[n - 20];
        if ( opp_fgt == rock)          { rcount--; }
        else if ( opp_fgt == paper)    { pcount--; }
        else /* opp_fgt == scissors */ { scount--; }
      }
    }
    total = rcount+pcount+scount;

    rstat = (rcount + 1.0)/(total + 3.0);
    pstat = (pcount + 1.0)/(total + 3.0);
    sstat = (scount + 1.0)/(total + 3.0);

    if (n < 20) {
      return( random() % 3);
    } 

    if (rstat > 0.45) { 
      return(paper); 
    } else if ( pstat > 0.45) { 
      return(scissors);
    } else if ( sstat > 0.45) {
      return(rock);
    } 
        
    for (i = 0; i < 27; i++) {
      patCount[i] = 0;
      for (j = 0; j < 3; j++)
        pat[i][j] = 0.0;
    }
    
    for (i = 1; i < n-1; i++) {
      pi = 0;
      b = 1;
      for (j = 0; j < 3; j++) {
        x = opp_history[i+j];
        pi += b*x;
        b *= 3;
      }
      if (i < n-2) {
        pat[pi][opp_history[i+3]] += 1;
        patCount[pi]++;
      }
    }
    for (i = 0; i < 27; i++)
    for (j = 0; j < 3; j++)
      pat[i][j] = (pat[i][j] + 1.0) / (patCount[i] + 3.0);

    for (j = 0; j < 3; j++)
      probs[j] += pat[pi][j];
      
    for (j = 0; j < 3; j++)
      if (pat[pi][j] > 0.45) {
        if (j == rock)
          return paper;
        else if (j == paper)
          return scissors;
        else
          return rock;
      }


    for (i = 0; i < 27; i++) {
      mypatCount[i] = 0;
      for (j = 0; j < 3; j++)
        mypat[i][j] = 0.0;
    }
    
    for (i = 1; i < n-1; i++) {
      pi = 0;
      b = 1;
      for (j = 0; j < 3; j++) {
        x = my_history[i+j];
        pi += b*x;
        b *= 3;
      }
      if (i < n-2) {
        mypat[pi][opp_history[i+3]] += 1;
        mypatCount[pi]++;
      }
    }
    for (i = 0; i < 27; i++)
      for (j = 0; j < 3; j++)
        mypat[i][j] = (mypat[i][j] + 1.0) / (mypatCount[i] + 3.0);
    
    for (j = 0; j < 3; j++)
      my_probs[j] += pat[pi][j];
      
    for (j = 0; j < 3; j++)
      if (mypat[pi][j] > 0.45) {
        if (j == rock)
          return paper;
        else if (j == paper)
          return scissors;
        else
          return rock;
      }

    rstat += (probs[rock] + my_probs[rock])/3.0;
    pstat += (probs[paper] + my_probs[paper])/3.0;
    sstat += (probs[scissors] + my_probs[scissors])/3.0;

    return(biased_roshambo(sstat,rstat));
}
/**********************************************************************/


/*  Entrant:  Bugbrain (12) and Knucklehead (52)   Sunir Shah (Can)

 I released the source code to Bugbrain and Crazybot in comp.ai.games.
 I hereby donate the code to the the tournament to be used for any purpose
 it wishes except for a) allowing someone else to enter the bot under their
 name, b) allowing distribution of the code without a byline that reads
 
 Sunir Shah's Roshambo bots [Sept'99].
 
 There are no guarantees these bots will do anything positive or
 negative.
 
 You may distribute this code as long as this comment exists in the source
 file. You may NOT enter any of these bots in any competition under any
 name but mine or without my permission.
 
 I can be contacted at sshah@intranet.ca.
 
 I suspect Bugbrain would be a better test to weed out weak bots than say
 Iocaine Powder! Bugbrain detects and exloits bots that have inheritantly
 static (and thus weak) strategies. cf. my post in comp.ai.games.
*/

/* -----------------------------------------------------------
**                     SUNIR'S ENTRIES
** -----------------------------------------------------------
*/

/* Uncomment to have the bots track information between 
** tournaments

#define sunPERSISTANT
*/

/* ----------------------------------------- Sunir's Utilities */

#define sunMYPREVTURN(x) (my_history[my_history[0] - (x) + 1])
#define sunOPPPREVTURN(x) (opp_history[opp_history[0] - (x) + 1])

#define sunMYLASTTURN sunMYPREVTURN(1)
#define sunOPPLASTTURN sunOPPPREVTURN(1)

#define sunNUMELEM(x) (sizeof (x) / sizeof *(x))

#define sunPI 3.141592654

/* Returns -1 on a loss, 0 on a tie, 1 on a win */
int sunRoshamboComparison( int me, int opp )
{
    static int aiCompareTable[] = {
        paper, /* rock */
        scissors, /* paper */
        rock, /* scissors */
    };

    if( me == opp )
        return 0;

    return (aiCompareTable[me] == opp) ? -1 : 1;
}

typedef struct 
{
    int iCurrentPlayer;
} sunPLAYERTRACKER;

/* Keeps track of which player I'm playing against */
int sunTrackPlayer( sunPLAYERTRACKER *pTracker  )
{
    if( !pTracker )
        return 0;

    if( !my_history[0] )
    {
        pTracker->iCurrentPlayer = (pTracker->iCurrentPlayer + 1) % players;
    }

    return pTracker->iCurrentPlayer;
}

/* ------------------------------------------ Sunir's Crazybot */

typedef struct
{
    int bInitialized;
    int iLastTurn;
    int aiTransform[3];
    double dShuffleProbability;
} sunCRAZYBOT;

/* Sets the transform table to a new random ordered set */
void sunShuffleCrazybotPlayer( sunCRAZYBOT *pPlayer )
{       
    int i = 3;
    while( i-- )
        pPlayer->aiTransform[i] = biased_roshambo(1.0/3,1.0/3);

    pPlayer->dShuffleProbability = 0.0;
}

void sunInitializeCrazybotPlayer( sunCRAZYBOT *pPlayer )
{
    pPlayer->bInitialized = 1;
    sunShuffleCrazybotPlayer( pPlayer );
}

/* If it ain't winnin', it might just punch itself in the head
** outta shear crazyness.
*/
int sunCrazybot()
{
#if defined(sunPERSISTANT)
    static sunCRAZYBOT aPlayers[players]; /* = {0}; */

    /* Created to get rid of GCC warning for above commented code */
    static int bPlayerArrayZeroed = 0;

    static sunPLAYERTRACKER Tracker = {0};

    sunCRAZYBOT *pPlayer = &aPlayers[sunTrackPlayer(&Tracker)];

    if( !bPlayerArrayZeroed )
    {
        bPlayerArrayZeroed = 1;
        memset( aPlayers, 0, sizeof aPlayers );
    }
#else
    static sunCRAZYBOT Player;
    sunCRAZYBOT *pPlayer = &Player;

    /* Reset the player data if we're on a new player */
    if( !my_history[0] )
        pPlayer->bInitialized = 0;
#endif

    if( !pPlayer->bInitialized )
        sunInitializeCrazybotPlayer( pPlayer );

    if( my_history[0] )
    {
        int iResult = sunRoshamboComparison( sunMYLASTTURN, sunOPPLASTTURN );

        if( iResult < 0 )
            pPlayer->dShuffleProbability += 0.1;
        else if( iResult == 0 )
            pPlayer->dShuffleProbability += 0.05;
    }

    if( flip_biased_coin( pPlayer->dShuffleProbability ) )
        sunShuffleCrazybotPlayer( pPlayer );

    return pPlayer->iLastTurn = pPlayer->aiTransform[pPlayer->iLastTurn];
}

/* ------------------------------------------ Sunir's Nervebot */

typedef struct 
{
    int bInitialized;

    /* [ways of arranging my last turn]
    ** [ways of arranging opponent's last turn]
    ** [ways of arranging my next turn]
    */
    double adProbabilities[3][3][3];    
} sunNERVEBOT;

/* Sets the player's matrix to initially random probabilities,
** taking care to ensure the probabilities sum to 1.0 for each
** input vector.
*/
void sunInitializeNervebotPlayer( sunNERVEBOT *pPlayer )
{       
    int i, j;

    pPlayer->bInitialized = 1;

    for( i = 3; i--; )
        for( j = 3; j--; )
        {
            pPlayer->adProbabilities[i][j][0] = 
                (double)random() / (double)maxrandom;

            pPlayer->adProbabilities[i][j][1] =
                ((double)random() / (double)maxrandom)
                    * (1.0 - pPlayer->adProbabilities[i][j][0]);

            pPlayer->adProbabilities[i][j][2] =
                1.0 
                - pPlayer->adProbabilities[i][j][0] 
                - pPlayer->adProbabilities[i][j][1];                     
        }
}

/* These are magic numbers */
double sunNerveAttenuateLoss( double dValue )
{
    /* Pulls value towards 0.0 */
    return dValue * 0.8;
}

double sunNerveAttenuateTie( double dValue )
{
    /* Pulls value towards 0.0 */
    return dValue * 0.9;
}

double sunNerveAttenuateWin( double dValue )
{
    /* Pulls value towards 1.0 but never exceeds 1.0 */
    return (dValue - 1.0) * 0.8 + 1.0;
}

/* Uses a nervous network whose input vector is 
** (my last turn, opponents last turn)
*/
int sunNervebot()
{
    /* Attenuate from last turn */
    int iResult = sunRoshamboComparison(sunMYLASTTURN, sunOPPLASTTURN);

    static double (*apfnAttenuations[])( double dValue) = {
        sunNerveAttenuateLoss,
        sunNerveAttenuateTie,
        sunNerveAttenuateWin,
    };

    double dDelta;
    int iNextProbability, iOtherProbability;
    double dNextProbability, dOtherProbability;

#if defined(sunPERSISTANT)      
    static sunNERVEBOT aPlayers[players]; /* = {0}; */

    /* Created to get rid of GCC warning for above commented code */
    static int bPlayerArrayZeroed = 0;  

    static sunPLAYERTRACKER Tracker = {0};

    sunNERVEBOT *pPlayer = &aPlayers[sunTrackPlayer(&Tracker)];

    if( !bPlayerArrayZeroed )
    {
        bPlayerArrayZeroed = 1;
        memset( aPlayers, 0, sizeof aPlayers );
    }
#else
    static sunNERVEBOT Player;
    sunNERVEBOT *pPlayer = &Player;

    /* Reset the player data if we're on a new player */
    if( !my_history[0] )
        pPlayer->bInitialized = 0;
#endif

    if( !pPlayer->bInitialized )
        sunInitializeNervebotPlayer( pPlayer );

    /* First turn */
    if( !my_history[0] )
        return biased_roshambo(1.0/3,1.0/3);

    /* Reward/punish based on last turn's vector and result */
    dDelta = pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][sunMYLASTTURN];

    pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][sunMYLASTTURN]
        = apfnAttenuations[iResult+1](dDelta);

    dDelta -= pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][sunMYLASTTURN];

    /* Propogate the delta throughout the remaining probabilities */
    iNextProbability = (sunMYLASTTURN + 1) % 3;
    iOtherProbability = (iNextProbability + 1) % 3;

    dNextProbability = pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][iNextProbability];
    dOtherProbability = pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][iOtherProbability];

    /* Distributes the delta weighted to the magnitude of the
    ** two other choices' respective probabilities
    */
    dDelta = dDelta * dNextProbability / (dNextProbability + dOtherProbability);

    pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][iNextProbability]
        += dDelta;

    pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][iOtherProbability] =
        1.0 
        - pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][iNextProbability]
        - pPlayer->adProbabilities[sunMYPREVTURN(2)][sunOPPPREVTURN(2)][sunMYLASTTURN];

    /* React to new vector */
    return biased_roshambo( 
        pPlayer->adProbabilities[sunMYLASTTURN][sunOPPLASTTURN][rock],
        pPlayer->adProbabilities[sunMYLASTTURN][sunOPPLASTTURN][paper] );
}

/* ------------------------------------------- Sunir's #undefs */

#undef sunMYLASTTURN
#undef sunOPPLASTTURN 

#undef sunMYPREVTURN
#undef sunOPPPREVTURN 

#undef sunNUMELEM

#undef sunPI

#if defined(sunPERSISTANT)
#undef sunPERSISTANT
#endif

/**********************************************************************/


/*  Entrant:  Psychic Friends Network   Michael Schatz et al (USA)
              (Unofficial Super-Modified Class, i.e. it cheats)

 note: may cause a Segmentation Fault vs MegaHAL (error: "OUCH")

 > The Psychic Friends Network is a truly hilarious piece of obfuscated C,
 > written by Michael Schatz and company at RST Corporation.  Among other
 > things, it uses an auxiliary function to find good karma, consults
 > horoscopes, cooks spaghetti and (mystic) pizza to go with various kinds
 > of fruit, #defines democrats as communists, and undefines god.  We're
 > still trying to figure out exactly what it is doing with the stack
 > frame, but we do know that it never scores less than +998 in a match,
 > unless it is playing against a meta-meta-cheater.
 
 To give credit, where credit was due:  Frank Hill and T.J. Walls
 (also of Reliable Software Technologies) were the other minds behind
 Psychic Friends Network.  To see some of their other exploits check out:
 http://www.rstcorp.com/news/gambling.html
*/

#ifdef Comment_Block  /* this funky code causes compiler warnings */

#define RST_ULTIMATE_ANALYZER_FUNCTION rst_ultimate_analyzer_function
#define GOD %
#define democrats communists
/* The open brace was always overrated anyway. */
#define recycle return

/* more readable */
#define THEFUNCTIONSTARTS {
#define THEIFSTARTS {
#define THELOOPSTARTS {
#define spaghetti RST_ULTIMATE_ANALYZER_FUNCTION
#define fresh (
#define rotten (unsigned
#define bananas int)
#define grapes bananas
#define sake 3
#define be_good_for random()

char *find_goodkarma(int *arr) THEFUNCTIONSTARTS
    int turn = arr[0], * karma[50], eleven = 0;
    int magic_bacon;

    *karma = &turn;
    while (!eleven) THELOOPSTARTS

        /* We need to determine the karma rating of the magic bacon. */
        /* This depends highly on the number eleven. */
        for (magic_bacon = 0; magic_bacon < turn; magic_bacon++) THELOOPSTARTS
            eleven = 1;
            if ( (*(*karma + magic_bacon)) != arr[magic_bacon] ) THEIFSTARTS
                eleven = 0;
                break;
            }
        }

        /* why does everyone put their comments at the end of the line? */
        /* is it eleven yet? */             if (eleven) break;
        /* determine karma ratio */         (0[karma]) += (fresh bananas * karma / fresh grapes * karma );
    }

    /* return the . . . whatever the heck this is. */    recycle (char *)*karma;
}

int RST_ULTIMATE_ANALYZER_FUNCTION() THEFUNCTIONSTARTS
    int turn [1];
    int *good_hand, *bad_hand, *pizza;
    int cancer, scorpio, libra;
    /* x is actually my all time favorite variable */     int x;
    int i, democrats;
    int (*callback) () = spaghetti;

    (*&cancer) = (scorpio = (libra = (int)NULL));
        *turn = opp_history[0];

        if (*turn < trials - 2) return libra ? callback() : be_good_for GOD sake;

    /* Consult appropriate astrological signs in order to determine exactly */
    /* which hand to throw. */
    good_hand = (int *)find_goodkarma(my_history);
    bad_hand = (int *)find_goodkarma(opp_history);

    if( cancer == 1 ) return *(int *)"ROCK";
    if( scorpio == 1 ) return *(int *)"SCISSORS";
    if( !(( scorpio != 0 ) || (cancer != 1)) || !((cancer != 0) ||
           (scorpio!=1)) ) return *(int *)"PAPER";
    if( ((  scorpio == 0 ) && (cancer == 1)) || ((cancer == 0) &&
           (scorpio==1)) ) return *(int *)"FONZ";

    /* Process Good Karma Values */
    for (i = 1; i<=*turn; i++) THELOOPSTARTS
        if (good_hand[i] == bad_hand[i]) libra++;
        else if ( ((good_hand[i] - bad_hand[i] +3) GOD sake) == 1) cancer++;
        else scorpio++;

        good_hand[i] = (bad_hand[i] + 1) GOD sake;
    }

    if (bad_hand > good_hand) THEIFSTARTS
        i = cancer;
        cancer = scorpio;
        scorpio = i;
        democrats = 2;
    }
    else democrats = 1;

    pizza = turn;
    for ( x = 0; !( (pizza[0] == libra) &&
        (pizza[1] == scorpio) &&
        (pizza[2] == cancer) ); x++ ) pizza++;

    pizza[0] = 0;
    pizza[1] = 0;
    pizza[2] = 0;
    pizza[3-democrats] = cancer + scorpio + libra;
    democrats = 0;

    recycle (pizza[democrats] + rotten bananas good_hand) GOD sake;
}

# undef GOD
/* Is that possible? */
#undef democrats
#undef recycle
#undef THEFUNCTIONSTARTS
#undef THEIFSTARTS
#undef THELOOPSTARTS
#undef spaghetti
#undef fresh
#undef rotten
#undef bananas
#undef grapes

#endif /* end of Comment_Block -- end of offending code */

/**********************************************************************/

/*  End of RoShamBo Player Algorithms  */


void Init_Player_Table (Player_Table crosstable[players+1])
{
    int i, j;

    i = 0;  /* list of players in the tournament */
    strcpy(crosstable[i].name, "Player Name");

    i++;  /* YOMI AI */
    strcpy(crosstable[i].name, "Yomi AI");
    if (usePython)
        crosstable[i].pname = python;
    else
        crosstable[i].pname = yomi;

#ifdef Comment_Block
#endif 
    i++;  /* choose uniformly at random */
    strcpy(crosstable[i].name, "Random (Optimal)");
    crosstable[i].pname = randbot;

    i++;  /* 20% rock, 20% paper, 60% scissors, randomly */
    strcpy(crosstable[i].name, "R-P-S 20-20-60");
    crosstable[i].pname = r226bot;

#ifdef Comment_Block  /* use these to comment out a block of players */    
#endif /* end of Comment_Block -- be sure to change the #define players value */
    i++;  /* nuthin' beats rock */
    strcpy(crosstable[i].name, "Good Ole Rock");
    crosstable[i].pname = rockbot;

    i++;  /* rotate r -> p -> s */
    strcpy(crosstable[i].name, "Rotate R-P-S");
    crosstable[i].pname = rotatebot;


    i++;  /* beat opponent's last move */
    strcpy(crosstable[i].name, "Beat The Last Move");
    crosstable[i].pname = copybot;


    i++;  /* beat the most frequent opponent choice */
    strcpy(crosstable[i].name, "Beat Frequent Pick");
    crosstable[i].pname = freqbot2;

    i++;  /* never repeat the same move */
    strcpy(crosstable[i].name, "Always Switchin'");
    crosstable[i].pname = switchbot;

#ifdef Comment_Block  /* use these to comment out a block of players */
    i++;  /* choose according to the digits of Pi */
    strcpy(crosstable[i].name, "* Pi");
    crosstable[i].pname = pibot;

    i++;  /* repeat last play infrequently */
    strcpy(crosstable[i].name, "* Switch A Lot");
    crosstable[i].pname = switchalot;
#endif /* end of Comment_Block */

#ifdef Comment_Block  /* use these to comment out a block of players */
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
#endif /* end of Comment_Block */

#ifdef Comment_Block  /* drb: player list */

#endif /* end of Comment_Block */

    i++;  /* Dan Egnor (USA) */
    strcpy(crosstable[i].name, "Iocaine Powder");
    crosstable[i].pname = iocainebot;

#ifdef Comment_Block  /* drb: player list */
#endif
    i++;  /* Jakob Mandelson (USA) */
    strcpy(crosstable[i].name, "Phasenbott");
    crosstable[i].pname = phasenbott;

    i++;  /* Jason Hutchens (Aus) */
    strcpy(crosstable[i].name, "MegaHAL");
    crosstable[i].pname = halbot;

    i++;  /* Jonathan Schaeffer (Can) */
    strcpy(crosstable[i].name, "Biopic");
    crosstable[i].pname = biopic;

    i++;  /* Don Beal (UK) */
    strcpy(crosstable[i].name, "Simple Modeller");
    crosstable[i].pname = mod1bot;

    i++;  /* Don Beal (UK) */
    strcpy(crosstable[i].name, "Simple Predictor");
    crosstable[i].pname = predbot;

    i++;  /* Andreas Junghanns (Ger) */
    strcpy(crosstable[i].name, "Robertot");
    crosstable[i].pname = robertot;

    i++;  /* Jack van Rijswijk (Net) */
    strcpy(crosstable[i].name, "Boom");
    crosstable[i].pname = boom;

    i++;  /* Dan Bothell, C Lebiere, R West (USA) */
    strcpy(crosstable[i].name, "ACT-R Lag2");
    crosstable[i].pname = actr_lag2_decay;

    i++;  /* Markian Hlynka (Can) */
    strcpy(crosstable[i].name, "Majikthise");
    crosstable[i].pname = markov5;

    i++;  /* Markian Hlynka (Can) */
    strcpy(crosstable[i].name, "Vroomfondel");
    crosstable[i].pname = markovbails;

    i++;  /* Aaron Davidson (Can) */
    strcpy(crosstable[i].name, "Granite");
    crosstable[i].pname = granite;

    i++;  /* Aaron Davidson (Can) */
    strcpy(crosstable[i].name, "Marble");
    crosstable[i].pname = marble;

    i++;  /* Neil Burch (Can) */
    strcpy(crosstable[i].name, "ZQ Bot");
    crosstable[i].pname = zq_move;

    i++;  /* Lourdes Pena (Mex) */
    strcpy(crosstable[i].name, "Sweet Rocky");
    crosstable[i].pname = sweetrock;

    i++;  /* Lourdes Pena (Mex) */
    strcpy(crosstable[i].name, "Piedra");
    crosstable[i].pname = piedra;

    i++;  /* Thad Frogley (UK) */
    strcpy(crosstable[i].name, "Mixed Strategy");
    crosstable[i].pname = mixed_strategy;

    i++;  /* Mark James (Can) */
    strcpy(crosstable[i].name, "Multi-strategy");
    crosstable[i].pname = multibot;

    i++;  /* Rafael Morales (UK) */
    strcpy(crosstable[i].name, "Inocencio");
    crosstable[i].pname = inocencio;

    i++;  /* Peter Baylie (USA) */
    strcpy(crosstable[i].name, "Peterbot");
    crosstable[i].pname = peterbot;

    i++;  /* Sunir Shah (Can) */
    strcpy(crosstable[i].name, "Bugbrain");
    crosstable[i].pname = sunNervebot;

    i++;  /* Sunir Shah (Can) */
    strcpy(crosstable[i].name, "Knucklehead");
    crosstable[i].pname = sunCrazybot;
#if 0
#endif /* end of Comment_Block */

#ifdef Comment_Block  /* use these to comment out a block of players */

    i++;  /* Michael Schatz et al (USA) */
    strcpy(crosstable[i].name, "Psychic Friends N");
    crosstable[i].pname = RST_ULTIMATE_ANALYZER_FUNCTION;

#endif /* end of Comment_Block -- be sure to change the #define players value */

    if (i != players) {
       fprintf(stderr, " Error: Wrong number of players in tournament! (%d)\n", i);
       exit(1);
    }

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

    printf(" Match results (draw <= %d): \n\n", g_drawn);
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
            if ( mtable[i].result[j] > g_drawn ) {
                mtable[i].result[j] = 2;
                mtable[i].result[0] += 2;
            }
            else if ( mtable[i].result[j] < -g_drawn ) {
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
        
        // YOMI CHANGES
        if (verbose4 == 0 && i >= 1) 
        {   
            printf(" (playing the rest of the tournament)\n\n");
            break;
        }
        // YOMI CHANGES

    }

    for (i = 1; i <= players; i++) {
        crosstable[i].result[0] = 0;
        for (j = 1; j <= players; j++) {
            crosstable[i].result[0] += crosstable[i].result[j];
        }
    }
    if (verbose2) { Print_T_Results (crosstable); }
}

int yomiVariable1;
int initPython(int argc, char *argv[]);
void exitPython();

int main(int argc, char *argv[]) {
   // YOMI CHANGES
   // go.exe [training variable] [use python (0,1)]
   int error = initPython(argc, argv);
   if (error)
       return 1;

   verbose1 = isVerbose();
   if (verbose1 == -1)
       return 1;

   verbose4 = 1;// during development, we are not interested in our standing   
   
   yomiVariable1 = atoi(argv[1]);
   if (yomiVariable1 == 0)
       yomiVariable1 = 1;
   //printf("%i", yomiVariable1);

   if (argc > 2)
       usePython = atoi(argv[2]);
   
   printf("");  //print an empty string to init print. otherwise, printing in Python would delay the prints in C
   ///////////////
   
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
      /* Print_Sorted_Results (crosstable); */
      /* g_drawn = 50 / sqrt(i);  statistical match draw value */
      /* Print_Match_Results (crosstable); */
   }

   if (verbose4)
   {
       g_drawn = 50.6 / sqrt(tourneys);
       printf(" Final results (draw value = %d):\n", g_drawn);
       
       Print_Scaled_Results (crosstable);   
       Print_Match_Results (crosstable);
    }
   /* add one for luck (compare to last iteration)
   g_drawn++;
   Print_Match_Results (crosstable);
   */
   
   exitPython();
   return(0);
}

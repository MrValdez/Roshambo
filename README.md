This is the repository for MrValdez's doctorate dissertation. 

This is a work in progress and does not represent my final dissertation.

#DOI used in this repository

The Effectiveness of using a Historical Sequence-based Predictor Algorithm in the First International RoShambo Tournament: 

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.12617.png)](http://dx.doi.org/10.5281/zenodo.12617)

The Effectiveness of using a Modified "Beat Frequent Pick" Algorithm in the First International RoShambo Tournament: 

[![DOI](https://zenodo.org/badge/4406/MrValdez/Roshambo.png)](http://dx.doi.org/10.5281/zenodo.10478)

#License

For the source code, please check LICENSE for more information, but the quick summary is: The International RoShamBo Test Suite has their own license and our AI is under the MIT license.

The Python.dll binary is under the [Python license](https://docs.python.org/3/license.html).

#Core Dependencies
 - **gcc**. We used the unofficial windows binaries: rubenvb MinGW-w64 (gcc rubenvb-4.8.0).
 - **Python 3.x**. We used Python 3.3 32-bit.
 - **OS**. We used Windows 8 64-bit, but other than the batch files, the AI code should be cross-platform (note: untested).
 - **SIMD oriented Fast Mersenne Twister(SFMT)**. We used this library for the AI's RNG. The original code can be found [here](http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/SFMT/index.html)
 
#Tools dependencies
 - **Python 3.x**. We used Python 3.3 32-bit.
 - **matplotlib** and **numpy**. Used by *charts.py* to generate the charts.
 - **click**. Used by *parseScore.py* as a helper for arguments.
 - **pygame**. Used by *debugger.py* to display the debugger.
 - **roman**. Used by *evolve.py* to differentiate between two exact names.
 
#AI dependencies
 - **pykov**. Used by the Yomi Layer Selector subroutine to generate Markov Chains. Github repository can be found [here](https://github.com/riccardoscalco/Pykov).
 
#Supplied prerequisites

*python3.dll* and *libpython.a* are binary prerequisites and are supplied in this repository. 

*python3.dll* is part of the Python 3.3 package and can be downloaded at http://python.org. 

*libpython.a* can be built by using *.\python_c_api\compile_libpython.bat* and *pexports.exe*. More information about compiling can be found at *.\python_c_api\python_links.txt*
    
*compile_python.bat* is used for testing purposes. It compiles a simple python+c program. This is a simple program to check that the compiled binaries worked.

*SFMT libray* is used for the AI's RNG. The entire source code is included with no changes and can be found [online](http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/SFMT/index.html).

#International RoShamBo Test Suite changes
Here are the changes for the test suite. These modifications are necessary to allow the addition of our AI as well as accomodate our version of gcc.

##GCC rubenvb related changes
- **random()** calls **rand()**. **random()** does not exist in our gcc library
- **srandom()** calls **srand()**. 
- **maxrandom** is redefined to the hardcode value of 32767.0. **rand()** uses less bits than **random()**
- **bzero()** calls **memset()**

##International RoShamBo Test Suite changes
  - total number of players has been changed.
  - *verbose1*, *verbose2*, *verbose3* and *verbose4* has been changed to int (originally constants). This allows them to be changed via Python.
  - Because of a bug in the Shofar AI, it was modified. Shofar has a one-off bug which causes it to throw an exception (line 3021 in the unmodified source code). We sidestep the problem by modifying the assert, but note that the random numbers that causes the exception can sometimes return an invalid move (this is because Shofar is accessing memory that it has no business accessing). Luckily, the test suite will modulo the invalid move so we can run the tournament.
  
##International RoShamBo Test Suite changes to accomodate Python

*Python.c* holds the cPython interface and the RPS library.
  
At the start of **main()**, Python is initialized. The python function **isVerbose()** and the corresponding verbose variable is set.
  
The *argv* is checked. This contains the filename for the Yomi configuration file that will modify the AI's behavior (see the section below for more information).

Finally, Python interface is properly closed when the test suite exits.

#Yomi AI
This is the internal name of our AI before we decided to simplify the program for the first paper. The paper which refers to this version of the repository has a different name for the AI (Modified Beat Frequent Pick), but for all intents and purposes, the implementation and results are the same.

#AI-to-test suite

The file *yomi.py* contains the AI that the test suite will use.

##Basic AI structure

This is the entry point of the AI. The modified test suite will look for this file and the function **play()**. **play()** must return 0, 1, or 2 (which are the values for rock, paper, and scissors, respectively). **play()** has one parameter: the DNA parameter. This contains the Yomi Configuration.
 
This is an example of a simple **play()** function:

```
   def play(DNA):
    return 0
```

  The function **isVerbose()** must also exist. This function should return True if we want the test suite to print the play results of each turn.

  The function **shutdown()** must also exist. This function is called when the program is about to exit. Any cleanups that should be done should be called here.
  
##RPS library
The RPS ibrary contains the following functions related to the International RoShamBo Test Suite:

- **rps.getTurn()** returns the current turn. Range is *[0..maxturns - 1]*. If 0 is returned, then this is the first turn and no move has been played yet.

- **rps.myHistory(turn)** returns the AI's move at *turn*. Turn's range is between *[1..maxturns]*.

- **rps.enemyHistory(turn)** returns the enemy's move at *turn*. Turn's range is between *[1..maxturns]*.

- **rps.biased_roshambo(rockProb, paperProb)** returns 0, 1, or 2. This is determined by the parameters supplied. For example, **biased_roshambo(1.0, 0.0)** returns 0, 100% of the time while **biased_roshambo(0.4, 0.2)** will return 0, 1 or 2 at the probability of 40%, 20%, 40% respectively.    

- **rps.random()** returns a random number using the SFMT library. This is used rather than Python's **math.random()** to ensure consistency.

- **rps.randomRange()** functions similarly to **rps.random()** but returns a floating number between [0..1].

- **rps.enemyName()** returns name of current enemy. Used for debugging. Don't use this to check opponent's name when deciding the AI's move.

## Simplest example of AI-to-test suite interface

```
def play(param):
    """ This returns 0, 1, or 2 and is the main entry point """
    return 0

def SkeletonAI():
    """ This is the most basic AI that showcase the rps library """
    currentTurn = rps.getTurn()
    
    if currentTurn:
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
    
    return (rps.enemyHistory(currentTurn) + 1) % 3

def isVerbose():
    """If True is returned, print the result of each trial."""
    return False

```

#BeatFrequentPick.py
 For the purpose of the first paper, *yomi.py* will use the AI from *BeatFrequentPick.py*. Please refer to the first paper for more detail on this subsystem.

#PatternPredictor.py
 For the purpose of the second paper, *yomi.py* will use the AI from *PatternPredictor.py*. Please refer to the second paper for more detail on this subsystem.

#Yomi AI configuration file

 This is actually an INI file and parsed by the *configparser* built-in library. This configuration file changes the behavior of the AI. The sections are as follows:
 
- **[info]** contains general information on the configuration. *name* is used to identify this configuration.

- **[strategies]** contains the strategies that will be used. More than one strategy is allowed.

- **[strategy ranking]** contains the algorithm used to rank the strategy. Available options are *wilson-high, wilson-low, none*.

- **[predictors]** contains the predictors that will be used. More than one predictor is allowed. A predictor variant can be used by appending the variant after the predictor name, delimited by space.

- **[predictor ranking]** contains the algorithm used to rank the predictor. Available options are *wilson-high, wilson-low, none*.

- **[yomi preferences]** contains the probabilities used in the markov chain. *AB* is for the probability from Yomi Layer 1 to Yomi Layer 2, *BC* is for the probability from Yomi Layer 2 to 3, and so on. The probabilities must be within [0..1]. 

- **[yomi-score preferences]** contains the influence of the yomi's score in the yomi subroutine. The values are *A*, *B*, and *C*, referring to Yomi Layer 1, 2, and 3, respectively. The values must be within [0..1].
 
- **[yomi-score preferences weight]** *(optional)* is used to increase or decrease the influence of the yomi-score preference. The values must be within [0..1].
 
 An example of a configuration file is as follows:
 
```ini
[info]
name="Baseline"
[strategies]
# random, none
random
[strategy ranking]
# wilson-high, wilson-low, none
wilson-high
[predictors]
# PP ?, MBFP ?, rock, none
PP 1
PP 2
PP 3
PP 4
PP 5
PP 6
PP 7
PP 8
PP 9
PP 10
PP 11
PP 12
PP 13
PP 14
PP 15
PP 16
PP 17
PP 18
PP 19
PP 20
PP 21
PP 22
PP 23
PP 24
PP 25
PP 26
PP 27
PP 28
PP 29
MBFP 1
MBFP 2
[predictor ranking]
# wilson-high, wilson-low, none
wilson-high
[yomi preferences]
AA=1
AB=0.01
AC=0
BA=1.0
BB=0.3
BC=0.2
CA=1.0
CB=0.7
CC=0.1
[yomi-score preferences]
A=1.0                 # Highest influence
B=0.7                 # Mid influence
C=0.45                 # Lowest influence
[yomi-score preferences weight]
weight = 1.0
```
 
#Compiling the test suite
 Run the *compile.bat* to create **go.exe** which is the main program for our modified test suite. It is expected that gcc can be found in the *PATH* environment.
 
 We used the filename **go.exe** instead of **rsb-ts1.exe** to increase typing speed during development.

#Python scripts

##trainer.py
 Used to run the tournament simulation with different variants, create the CSV, and plot the charts.
 
 In the script code, *pathbase* is used to tell the script where the results will be stored. Note: this string should end with "/".

 The **main()** function runs the script. It was built this way to allow commenting out specific behavior for debugging purposes.
 
 The **Validate()** function will validate the configuration file before running the tournament. Refer above on how the configuration file works.
 
 The **PlayTournament()** function plays the tournament. Each configuration files in the input directory is run and the output will be saved with the same file name to an output directory.
 
 The **CreateCSV()** function will parse each result and create two csv files with the csv columns: variant variable, rank. The first csv file is for the "Match results" and the second is for the "Tournament results" ("**results_match.csv**" and "**results_tournament.csv**" respectively).
 
 The **charts.startPlotting()** function will create the chart graphics. Refer to charts.py.

##parseScore.py
 Used to study how many points (wins-loss-ties) the variant got compared to either all the bots or against a specific bot.
 
 In the script code, *pathbase* is used to tell the script where the results will be stored. Note: this string should end with /.

 The format is as follows:
```shell
Usage: parseScore.py [OPTIONS]

Options:
  --bot TEXT          Name of bot to parse
  --showresults TEXT  A value of True means the points gained from all variants are shown
  --showlatex TEXT    A value of True means that the code for a latex table is outputted instead.
  --help              Show this message and exit.
```

  **[bot]** is optional and contains the name of the bot (a part of the bot's name is enough). Does not accept space due to coding limitations, so use part of the bot's name to circumvent this (this can be fixed in the source code, but the partial name is good enough for the purpose of the research). 
  
  **[show results]** is optional. A value of True means the points gained from all variants are shown. Any other values gives the default behavior of not showing the results.
  
  **[show latex]** is optional. A value of True means that the code for a latex table is outputted instead.
  
###Example:
  To show all the results against all bots:
```shell
   python parseScore.py
```

  To show the results against the Iocaine bot:
```shell
   python parseScore.py --bot=Iocaine
```

  To show the results against the RPS 20-20-60 bot:
```shell
   python parseScore.py --bot=20-60
```
        
  To show the results against the RPS 20-20-60 bot and show our bot's scores with different variants:
```shell
   python parseScore.py --bot=20-60 --showresults=True
```

  To show all the results against all bots with latex output:
```shell
   python parseScore.py --showresults=False --showlatex=True
```

##parseLatex.py
  Used to create the \LaTeX tables from the results of the bots found in a specified directory. The \LaTeX tables are saved in a .tex file in the output directory.
 
  Note that to change the behavior for this script, it has to be directly modified. Also note the trailing slash at the end of the path.
 
  For example, to create the latex for the input and output directory, we use the following modifications:
```shell
 ParseLatex(path_input = "input/", path_output = "output/")
```

   
##charts.py
 Used to generate a matplot chart from the csv generated by *trainer.py*
 
 When used from the command prompt, it generates a matplot chart from "**results_match.csv**" and "**results_tournament.csv**", and saves it as "**results_match.png**" and "**results_tournament.png**"
 
When imported as a library, you can call the **Plot()** function. It has the following parameters:
```
  Plot(filename, title, saveFigure = True)
```

##debugger.py
 Creates a server that receives data from a running instance of *yomi.py*. This program will display a pygame window that shows what Yomi Layer was used against a specific AI at a specific turn. 
 
 A turn is represented by a 10x10 tile. The tile's color represents the Yomi Layer used in that turn. The colors are:
 
- Layer 0: Red
- Layer 1: Green
- Layer 2: Blue
- Layer 3: Magenta (255 Red, 0 Green, 255 Blue)
 
 The arrow keys are used to move the debugger. Restarting the simulation will not clear the debugger but will overwrite the tiles, one line at a time. The [ and ] keys will zoom in and zoom out, respectively.

This is the repository for MrValdez's doctorate dissertation. Once the first paper is published, it will be linked to this repository. 

This is a work in progress and does not represent the final dissertation.

#License

For the source code, please check LICENSE for more information, but the quick summary is: The International RoShamBo Test Suite has their own license and our AI is under the MIT license.

The Python.dll binary is under the [Python license](https://docs.python.org/3/license.html)

#Dependencies
 - **gcc**. We used the unofficial windows binaries: rubenvb MinGW-w64 (gcc rubenvb-4.8.0).
 - **Python 3.x**. We used Python 3.3 32-bit.
 - **OS**. We used Windows 8 64-bit, but other than the batch files, this code should be cross-platform (note: untested).

#Supplied prerequisites

*python3.dll* and *libpython.a* are binary prerequisites and are supplied in this repository. 

python3.dll is part of the Python 3.3 package and can be downloaded at http://python.org. 

libpython.a can be built by using *.\python_c_api\compile_libpython.bat* and *pexports.exe*. More information about compiling can be found at *.\python_c_api\python_links.txt*
    
*compile_python.bat* is used for testing purposes. It compiles a simple python+c program. This is a simple check that the compiled binaries worked.

#International RoShamBo Test Suite changes
Here are the changes for the test suite. These modifications are necessary to allow the addition of our AI as well as accomodate our version of gcc.

##GCC specific changes
- **random()** calls **rand()**. **random()** does not exist in our gcc library
- **srandom()** calls **srand()**. 
- **maxrandom** is redefined to the hardcode value of 32767.0. **rand()** uses less bits than **random()**
- **bzero()** calls **memset()**

##International RoShamBo Test Suite changes
  - not included in this revision's results: *Pi, Switch A Lot, Flat, Anti-Flat, Foxtrot, De Bruijn, Text, Anti-rotn, Copy-drift, Add-react, Add-drift*.
  - One AI was changed for the purpose of this paper: shofar. Shofar, for some odd reason, is throwing an run-time exception. A quick debug shows that the python-c api is causing this problem. To complete the tournament, the assert (line 3055) has been commented. This will be returned later. (todo: solve this mystery)
  - total number of players has been changed.
  - *verbose1*, *verbose2*, *verbose3* and *verbose4* has been changed to int (originally constants). This allows them to be changed via Python.
  
##Python specific changes
*Python.c* holds most of the Python interface
  
At the start of **main()**, Python is initialized. The python function **isVerbose()** and the corresponding verbose valuable is set.
  
The *argv* is checked:

- The *first argv* is the variable constant. 

- The *second argv* is an integer taking 0 or 1. If a value of non-1 is given, it will not use the Python code. This is used during debugging to check our Python code against the C code.

Finally, Python is properly closed when the test suite exits.

#Yomi AI
This is the internal name of our AI before we decided to simplify the program for the first paper. The paper which refers to this version of the repository has a different name for the AI (Modified Beat Frequent Pick), but for all intents and purposes, the implementation and results are the same.

#yomi.py

##Basic structure

This is the entry point of the AI. The modified test suite will look for this file and the function **play()**. **play()** must return 0, 1, or 2 (which is the value for rock, paper, and scissors, respectively). **play()** must also accept one parameter. This is the parameter that is sent by the trainer program.
 
This is an example of a simple **play()** function:

```
   def play(param):
    return (param + 1) % 3
```

  The function **isVerbose()** is also needed. This function should return True if we want the test suite to print the play results of each turn.
  
The rps library contains the following test suite related functions:

- **rps.getTurn()** returns the current turn. Range is *[0..maxturns - 1]*. If 0 is returned, then this is the first turn and no move has been played yet.

- **rps.myHistory(turn)** returns the AI's move at turn. Turn's range is between *[1..maxturns]*.

- **rps.enmeyHistory(turn)** returns the enemy's move at turn. Turn's range is between *[1..maxturns]*.

- **rps.biased_roshambo(rockProb, paperProb)** returns 0, 1, or 2. This is determined by the parameters supplied. For example, **biased_roshambo(1.0, 0.0)** returns 0, 100% of the time while **biased_roshambo(0.4, 0.2)** will return 0, 1 or 2 at the probability of 40%, 20%, 40% respectively.    

- **rps.random()** returns a random number using the test suite's random function. We should use this rather than Python's **math.random()** to ensure that we are using the same RNG as the AIs in the test suite. We theorized that Python's math library will also use the same RNG as the test suite, but we did not test for this.

#BeatFrequentPick.py
 Pleaes refer to the first paper we have developed for the Yomi AI for more details on this subsystem.
 
#Compilation of the test suite
 Run the compile.bat to create **go.exe** which is the main program for our modified test suite. It is expected that gcc can be found in the *PATH* environment.
 
 We used the filename **go.exe** instead of **rsb-ts1.exe** to increase typing speed during development.

#Python script helpers

##trainer.py
 Used to play the tournament, create the CSV and plot the charts.
 
 In the script code, pathbase is used to tell the script where the results will be stored. Note: this string should end with "/".

 The **main()** function runs the script. It is built this way to allow commenting specific behavior for debugging purposes.
 
 The **PlayTournament(size)** function plays the tournament. Size refers to the maximum number of variants that will play. From the size variable, the variants are created with values of **[1..size + 1]**. In our modified RoShamBo Test Suite, these variants are then passed via argv. The results are saved into "results %s.txt" where %s is the variant number.
 
 The **CreateCSV()** function will parse each result and create two csv files with the format: variant variable, rank. The first csv file is for the "Match results" and the second is for the "Tournament results".
 
 The **charts.startPlotting()** function will create the chart graphics. Refer to charts.py.

##parseScore.py
 Used to study how many points (wins-losts-ties) our bot got compared to another bot.

 In the script code, pathbase is used to tell the script where the results will be stored. Note: this string should end with "/".
  
 The format is as follows:
```shell
  parseScore.py [botname] [show all results]
```

  **[botname]** is optional and contains the name of the bot (a part of the bot's name is enough). Does not accept space, use part of the name to circumvent this.

  **[show all results]** is optional. A value of 1 means the points gained from all variants are shown. Any other values gives the default behavior of not showing the results.
  
###Example:
  To show the results against the Iocaine bot:
```shell
   python parseScore.py Iocaine
```

  To show the results against the RPS 20-20-60 bot:
```shell
   python parseScore.py 20-60
```
        
  To show the results against the RPS 20-20-60 bot and show our bot's scores with different variants:
```shell
   python parseScore.py 20-60 1
```
   
##charts.py
 Used to generate a matplot chart from the csv generated by trainer.py
 
 When used from the command prompt, it generates a matplot chart from "results_match.csv" and "results_tournament.csv", and saves it as "results_match.png" and "results_tournament.png"
 
When imported as a library, you can call the **Plot()** function. It has the following paramters:
```
  Plot(filename, title, saveFigure = True)
```

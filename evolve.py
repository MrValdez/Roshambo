# "Genetic algorithms are often applied as an approach to solve global optimization problems." - wki

# Select DNA folder from database
# Clone DNA
# Mutate DNA
# Play tournament with DNA
# Save
# Repeat

import os
import random
import configparser
import string
import shutil
import roman
import time

import trainer

Debug = True
Debug = False

basedir = "DNAVillage/"

# (category, key, should have [0-1] limit?)
Genes = [("yomi preferences", ("AA", "AB", "AC", "BA", "BB", "BC", "CA", "CB", "CC"), True),
         ("yomi-score preferences", ("A", "B", "C"), False)]

with open("movie-characters.txt", "r") as f:
    FirstNames = f.read()
    FirstNames = FirstNames.split("\n")
    
    #skip the first 4 lines
    FirstNames = FirstNames[4:]
    
    # don't use names with the symbols ,?/\
    FirstNames = [name for name in FirstNames if name.find(",") == -1]
    FirstNames = [name for name in FirstNames if name.find("?") == -1]
    FirstNames = [name for name in FirstNames if name.find("/") == -1]
    FirstNames = [name for name in FirstNames if name.find("\\") == -1]
    
with open("Family-Names.txt", "r") as f:
    LastNames = f.read()
    LastNames = LastNames.split("\n")

def SelectDNA():
    # get the latest generation number
    generations = [directory.split("_")[1] for directory in os.listdir(basedir) if os.path.isdir(basedir + directory)]
    generations = [int(generations) for generations in generations]

    currentGeneration = max(generations)
    currentGeneration = str(currentGeneration)

    return currentGeneration
    
def GeneratePaths(currentGeneration):    
    old_path_input  = basedir + "input_"  + currentGeneration + "/"
    old_path_output = basedir + "output_" + currentGeneration + "/"
    
    # check if path exist. If it doesn't, throw an exception
    if not (os.path.isdir(old_path_input) and os.path.isdir(old_path_output)):
        raise Exception("%s, %s not found" % (old_path_input, old_path_output))

    # check if old path input is not marked. If it is, throw an exception
    if (os.path.isfile(old_path_input + "unmutated") or 
        os.path.isfile(old_path_input + "mutating")):
        raise Exception("%s has a unmutated/mutating mark. Possible reason: MutateDNA was interrupted" % (old_path_input))
        
    currentGeneration = int(currentGeneration)
    new_path_input  = basedir + "input_"  + str(currentGeneration + 1) + "/"
    new_path_output = basedir + "output_" + str(currentGeneration + 1) + "/"

    # check if path already exists. If it does, throw an exception
    if os.path.isdir(new_path_input) or os.path.isdir(new_path_output):
        raise Exception("%s, %s already exists" % (new_path_input, new_path_output))

    return new_path_input, new_path_output, old_path_input, old_path_output

def CloneDNA(new_path_input, new_path_output, old_path_input, old_path_output):
    # create directory
    os.mkdir(new_path_input)
    os.mkdir(new_path_output)
    
    # copy the files in the old path to the new path
    for file in os.listdir(old_path_input):
        shutil.copy(old_path_input + file, new_path_input)

    for file in os.listdir(old_path_output):
        shutil.copy(old_path_output + file, new_path_output)
    
    # add a file to mark the input as "unmutated"
    with open(new_path_input + "unmutated", "w") as f:
        f.write(old_path_input)
        f.write(old_path_output)
    

def _EvaluateDNA(filename):
    # This returns the fitness of an individual
    # We evaluate using the match ranking, the tournament ranking, and the tournament points
    # with a higher priority for match ranking.
    # We get the inverse of the tournament points since we sort via the lowest.
    matchRankStr      = "Yomi AI is match ranked "
    tournamentRankStr = "Yomi is tournament ranked "
    tournamentResultStr = """ Tournament results:
    Player Name          total 
  1 Yomi AI"""

    with open(filename, "r") as f:
        text = f.read()
        found = text.find(matchRankStr)
        if found == -1:
            raise Exception ("match rank not found")
        matchRank = text[found + len(matchRankStr):text.find("\n", found)]
        
        found = text.find(tournamentRankStr)
        if found == -1:
            raise Exception ("tournament rank not found")
        tournamentRank = text[found + len(tournamentRankStr):text.find("\n", found)]
        
        found = text.find(tournamentResultStr)
        if found == -1:
            raise Exception ("tournament points not found")
        tournamentPoints = text[found + len(tournamentResultStr):text.find("\n", found + len(tournamentResultStr))]
        tournamentPoints = tournamentPoints.strip()
        originalTournamentPts = tournamentPoints
        # 42 players * 1000        
        maxPoints = 42 * 1000
        tournamentPoints = str(maxPoints - int(tournamentPoints))
        
    rank = float("%s.%s%s" % (matchRank, tournamentRank.zfill(2), tournamentPoints.zfill(len(str(maxPoints)))))
    if Debug: print("%s rank: %s (%s %s %s)" % (filename, rank, matchRank, tournamentRank, originalTournamentPts))
    return rank, (int(matchRank), int(tournamentRank))

def WriteDNA(path_input, Name, newDNA):
    newFile = path_input + Name + ".txt"
    
    # Check if name already exists. If it does, add a generation indicator.
    if os.path.isfile(newFile):
        generation = 2
        while True:
            newFile = path_input + Name + "-" + roman.toRoman(generation) + ".txt"
            if not os.path.isfile(newFile):
                break
            generation += 1
            
    with open(newFile, "w") as f:
        newDNA.write(f)

    return newFile

def _FindMates(path_input, path_output):
    Population = os.listdir(path_input)
    
    # filter out mutating mark
    Population = [Population for Population in Population if Population != "mutating"]
    
    # Add fitness for each DNA.
    
    # We have two fitness evaluation, one for the ranking (match + tournament rank) and another for the tournament rank.
    # We do this so we won't lose individuals with a high tournament rank but low match rank.
    RankingPopulation = [[Population, _EvaluateDNA(path_output + Population)[0]] for Population in Population]
    RankingPopulation.sort(key = lambda a: a[1])

    PointsPopulation = [[Population, _EvaluateDNA(path_output + Population)[1]] for Population in Population]
    PointsPopulation.sort(key = lambda a: (a[1][1], a[1][0]))       # sort by tournament rank, then match rank
    PointsPopulation = [[Population[0], _EvaluateDNA(path_output + Population[0])[0]] for Population in PointsPopulation]
    
    Population = []
    
    # filter in the top ranking individuals (75%)
    maxPopulationSize = int((len(RankingPopulation) * 0.75))
            
    # Set the maximum population size to 25-32
    maxPopulationSize = min(maxPopulationSize, random.randint(25, 32))
    # Set the minimum population size to 10
    maxPopulationSize = max(maxPopulationSize, 10)

    AlphaIndividuals = RankingPopulation[0:maxPopulationSize]
    
    # add in the individuals from the high points population to the alpha individuals
    PointsPopulation = PointsPopulation[0:5]
    for individual in PointsPopulation:
        if not individual in AlphaIndividuals:
            AlphaIndividuals.append(individual)

    Population = AlphaIndividuals

    # delete the individuals that are not in the population
    ToPreserve = []
    AllFiles = set(os.listdir(path_input))
    
    for file, _ in Population:
        ToPreserve.append(file)
    ToDelete = set(ToPreserve).symmetric_difference(AllFiles)
    ToDelete.remove("mutating")
    
    for file in ToDelete:
        if Debug: print("deleting", file)
        os.remove(path_input + file)     
        os.remove(path_output + file)     
        
    for newIndividualSize in range(random.randint(3, 10)):
        # either create new individuals to the population, or mate
       
        # .15% chance the two will mate
        MatingTreshold = 0.15

        if random.uniform(0, 1) > MatingTreshold: 
            # Create new individual
            Mutating = random.choice(AlphaIndividuals)

            _CreateNewDNA(path_input, Mutating[0])
            newName, newDNA = _MutateDNA(path_input, Mutating)
            newName = _StrangerName()
            
            newFile = WriteDNA(path_input, newName, newDNA)
            if Debug: print("Writing mutated", newFile)
        
        else:
            # Let's mate two individuals

            # Grab two random individual with a bias for those with higher rank        
            a = random.triangular(0, 1, 0.2)
            b = random.triangular(0, 1, 0.6)
            Dominant = Population[int(a * len(Population))]
            Mate     = Population[int(b * len(Population))]
            
            # If we grabbed the same individual, just mutate it instead.
            if Dominant == Mate:
                newName, newDNA = _MutateDNA(path_input, Dominant)

                newFile = WriteDNA(path_input, newName, newDNA)
                maxPopulationSize -= 1
                if Debug: print("Writing mutated", newFile)

                continue
                        
            newName  = _MutateName(Dominant[0], Mate[0])
            newDNA   = _MateDNA(path_input, newName, Dominant, Mate)
            
            # write newDNA to file
            newFile = WriteDNA(path_input, newName, newDNA)
            if Debug: print("Writing mated", newFile)
        
def filterName(newLastName, newFirstName, newMiddleName):
    newLastName   = newLastName
    newFirstName  = newFirstName
    newMiddleName = newMiddleName
    
    return newLastName + ", " + newFirstName + " " + newMiddleName    
    
def _StrangerName():
    # Return a randomly generated name
    newLastName   = random.choice(LastNames)
    newMiddleName = random.choice(LastNames)
    newFirstName  = random.choice(FirstNames)
    
    newName = filterName(newLastName, newFirstName, newMiddleName)
    return newName        

def _MutateName(DominantName, MateName):
    # DominantName is the name of the individual with the most contribution.
    # MateName is the name of the individual mated with.
    
    # Names taken from:
    #  http://www.outpost9.com/files/WordLists.html
    #  http://deron.meranda.us/data/
    
    newLastName   = DominantName.split(",")[0]
    newMiddleName = MateName.split(",")[0]
    newFirstName  = random.choice(FirstNames)
    
    newName = filterName(newLastName, newFirstName, newMiddleName)
    return newName

def _ReadDNA(filename):
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform=str
    config.read(filename)       
    
    return config

def _MutateGene(mutationChance, geneRewriteChance, newDNA):    
    # mutate genes
    for gene, values, hasLimit in Genes:
        for value in values:
            if random.uniform(0, 1) < mutationChance:
                original_value = float(newDNA[gene][value].split("#")[0])
                delta = 1
                
                if random.uniform(0, 1) < geneRewriteChance:
                    delta = random.uniform(0, 1)
                    if Debug: print(" replacing", gene, value, delta)
                else:    
                    delta = random.uniform(-0.1, 0.1)
                    delta += original_value
                    
                    if Debug: print(" new", gene, value, delta)                
                 
                if not hasLimit:
                    # Gene has a range of [0-1]
                    delta = min(delta, 1.0)
                    delta = max(delta, 0.0)
                
                newDNA[gene][value] = str(delta)

    def shift(transition1, transition2, transition3):
        changed = False
        transition1, transition2, transition3 = float(transition1), float(transition2), float(transition3)
    
        if transition1 < 0:
            shift = abs(transition1)
            transition1 += shift
            transition2 += shift
            transition3 += shift
            changed = True
        if transition2 < 0:
            shift = abs(transition2)
            transition2 += shift
            transition2 += shift
            transition2 += shift
            changed = True
        if transition3 < 0:
            shift = abs(transition3)
            transition3 += shift
            transition3 += shift
            transition3 += shift
            changed = True
            
        return str(transition1), str(transition2), str(transition3), changed

    # The genes for the transition cannot be negative. However, the mutation code 
    # above allows for negative numbers. A negative number will "push" or shift
    # all other transition values forward

    newDNA["yomi preferences"]["AA"],   \
    newDNA["yomi preferences"]["AB"],   \
    newDNA["yomi preferences"]["AC"],   \
    changed =  \
    shift(newDNA["yomi preferences"]["AA"], newDNA["yomi preferences"]["AB"], newDNA["yomi preferences"]["AC"])
    
    if Debug and changed: 
        print(" Shifted yomi preferences. New values: \n  AA %s\n  AB %s\n  AC %s" % 
            (newDNA["yomi preferences"]["AA"], newDNA["yomi preferences"]["AB"], newDNA["yomi preferences"]["AC"]))
    
    newDNA["yomi preferences"]["BA"],   \
    newDNA["yomi preferences"]["BB"],   \
    newDNA["yomi preferences"]["BC"],   \
    changed =  \
    shift(newDNA["yomi preferences"]["BA"], newDNA["yomi preferences"]["BB"], newDNA["yomi preferences"]["BC"])

    if Debug and changed: 
        print(" Shifted yomi preferences. New values: \n  BA %s\n  BB %s\n  BC %s" % 
            (newDNA["yomi preferences"]["BA"], newDNA["yomi preferences"]["BB"], newDNA["yomi preferences"]["BC"]))
                
    newDNA["yomi preferences"]["CA"],   \
    newDNA["yomi preferences"]["CB"],   \
    newDNA["yomi preferences"]["CC"],   \
    changed =  \
    shift(newDNA["yomi preferences"]["CA"], newDNA["yomi preferences"]["CB"], newDNA["yomi preferences"]["CC"])

    if Debug and changed: 
        print(" Shifted yomi preferences. New values: \n  CA %s\n  CB %s\n  CC %s" % 
            (newDNA["yomi preferences"]["CA"], newDNA["yomi preferences"]["CB"], newDNA["yomi preferences"]["CC"]))    
            
    return newDNA

def _MateDNA(path_input, newName, Dominant, Mate):
    # Read both DNA
    DNA1 = _ReadDNA(path_input + Dominant[0])
    DNA2 = _ReadDNA(path_input + Mate[0])
    
    newDNA = DNA1
    newDNA["info"]["name"] = newName
    newDNA["info"]["Dominant Parent"] = Dominant[0]
    newDNA["info"]["Mate"] = Mate[0]
      
    # Select 90% of DNA from Dominant, the rest from Mate
    DominantGenesPer = 0.9
    
    for gene, values, hasLimit in Genes:
        for value in values:
            if newDNA[gene][value] != DNA2[gene][value] and \
               random.uniform(0, 1) < DominantGenesPer:
                if Debug: print(" Inheriting from mate", gene, value, DNA2[gene][value])
                newDNA[gene][value] = DNA2[gene][value]

    # 50% chance to mutate
    # 1% chance to completely change the gene value
    mutationChance = 0.5
    geneRewriteChance = 0.01
    newDNA = _MutateGene(mutationChance, geneRewriteChance, newDNA)
        
    # Check if new DNA will inherit from Mate
    predictors1 = set(DNA1["predictors"])
    predictors2 = set(DNA2["predictors"])
    
    # Have a 5% chance to inherit new predictor
    ChanceToInheritPredictor = 0.05
    
    for predictor in predictors1.symmetric_difference(predictors2):
        if not predictor in predictors1:
            #  Mate has predictor that is not in Dominant. Check if we inherit that predictor
            if random.uniform(0, 1) < ChanceToInheritPredictor:
                newDNA["predictors"][predictor] = None
                if Debug: print(" Inheriting predictor from mate", predictor)
     
    return newDNA
    
def _CreateNewDNA(path_input, filename):
    """ Create a new DNA with complete predictors and a default ranking system of 'wilson-high' """
    newDNA = _ReadDNA(path_input + filename)

    for i in range(1, 21 + random.randint(-4, +4)):
        newPredictor = "PP %i" % (i)
            
        if not newPredictor in newDNA["predictors"]:
            newDNA["predictors"][newPredictor] = None

    for i in range(1, 2 + random.randint(0, 2)):
        newPredictor = "MBFP %i" % (i)
            
        if not newPredictor in newDNA["predictors"]:
            newDNA["predictors"][newPredictor] = None

    rankingDNAs = ["strategy ranking", "predictor ranking"]

    for rankingDNA in rankingDNAs:
        defaultRankingSystem = "wilson-high"
        currentRankingSystems = [rank for rank in newDNA[rankingDNA]] 
        for rank in currentRankingSystems:
            if rank != defaultRankingSystem:
                newDNA.remove_option(rankingDNA, rank)
        
        if not defaultRankingSystem in newDNA[rankingDNA]:
            newDNA[rankingDNA][defaultRankingSystem] = None

    if Debug:
        print("Created new DNA for %s with predictors:" % (path_input))
        for p in newDNA["predictors"]:
            print (p, end =", ")
        print("")
    
def _MutateDNA(path_input, Original):
    # Generate the name of the mutation
    newLastName   = Original[0].split(",")[0]
    #newMiddleName = Original[0].split(" ")[-1].split(".")[0]
    newMiddleName = random.choice(LastNames)
    newFirstName  = random.choice(FirstNames)

    newName = filterName(newLastName, newFirstName, newMiddleName)

    # Read the DNA
    newDNA = _ReadDNA(path_input + Original[0])
    
    # Mutate the DNA
    newDNA["info"]["name"] = newName
    newDNA["info"]["Mutate From"] = Original[0].split(".")[0]
    
    # .1% chance to drop a predictor
    dropPredictorChance = 0.01
    for predictor in newDNA["predictors"]:
        if len(newDNA["predictors"]) and random.uniform(0, 1) < dropPredictorChance:
            if Debug: print(" removing", predictor)
            newDNA.remove_option("predictors", predictor)
            
    # 3% chance to add 1-10 new predictors
    newPredictorChance = 0.3
    newPredictorTries = 10
    if random.uniform(0, 1) < newPredictorChance:
        while newPredictorTries > 0:
            newPredictorTries -= 1
            
            newPredictor = random.choice(["MBFP", "PP"])
            newPredictor = "%s %i" % (newPredictor, random.randint(1, 32))
            
            if not newPredictor in newDNA["predictors"]:
                newDNA["predictors"][newPredictor] = None
                if Debug: print(" Adding new predictor:", newPredictor)
                newPredictorTries -= random.randint(1, 10)
    
    # 60% chance to mutate
    # 5% chance to completely change the gene value
    mutationChance = 0.60
    geneRewriteChance = 0.05
    newDNA = _MutateGene(mutationChance, geneRewriteChance, newDNA)
    
    # mutate ranking system
    # 0.1% chance to change ranking system
    changeRankingSystemChance = 0.01
    rankingDNAs = ["strategy ranking", "predictor ranking"]

    for rankingDNA in rankingDNAs:
        if random.uniform(0, 1) < changeRankingSystemChance:
            
            rankingSystems = ["wilson-low", "wilson-high"]
            newRankingSystem = random.choice(rankingSystems)
            
            if not newRankingSystem in newDNA[rankingDNA]:
                # add new ranking system. remove all ranking system that is not the new
                # system. We do it this way to preserve section order
                newDNA[rankingDNA][newRankingSystem] = None
                currentRankingSystems = [rank for rank in newDNA[rankingDNA]] 
                for rank in currentRankingSystems:
                    if rank != newRankingSystem:
                        newDNA.remove_option(rankingDNA, rank)
                
                if Debug: print("Changing %s from %s to %s" % (rankingDNA, currentRankingSystems, newRankingSystem))

    return newName, newDNA

def RunGA(path_input, path_output):
    # check for "unmutated" mark. If it doesn't exist, throw exception
    if not os.path.isfile(path_input + "unmutated"):
        raise Exception("%s do not have unmutated mark. Possible reason: MutateDNA was interrupted" % (path_input))
    
    # change "unmutated" mark to "mutating".
    os.rename(path_input + "unmutated", path_input + "mutating")
        
    _FindMates(path_input, path_output)
    
    # remove mark for "mutating".
    os.unlink(path_input + "mutating")
    
def main():
#    trainer.main(r"DNAVillage/input_1/", r"DNAVillage/output_1/")
    currentGeneration = SelectDNA()
    print ("Starting Generation", int(currentGeneration) + 1)
    
    new_path_input, new_path_output, old_path_input, old_path_output = GeneratePaths(currentGeneration)
    
    #check if we need to run trainer on the previous generation
    if len(os.listdir(old_path_output)) != len(os.listdir(old_path_input)):
        print ("Re-training previous generation (generation %s)" % (currentGeneration))
        trainer.main(old_path_input, old_path_output)
        print ("Restarting Generation", int(currentGeneration) + 1)

    if len(os.listdir(old_path_input)) == 0:
        raise Exception("Warning: Generation is empty. Double check folder")
        
    CloneDNA(new_path_input, new_path_output, old_path_input, old_path_output)
    RunGA(new_path_input, new_path_output)
    trainer.main(new_path_input, new_path_output)
    
if __name__ == "__main__":
    while True:
        startTimer = time.perf_counter()
        main()
        endTimer = time.perf_counter()
        elapsedTime = endTimer - startTimer
        print("Elapsed time: %f mins\n" % (elapsedTime / 60.0))
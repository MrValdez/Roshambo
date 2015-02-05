# "Genetic algorithms are often applied as an approach to solve global optimization problems." - wki

# Select DNA folder from database
# Clone DNA
# Mutate DNA
# Play tournament with DNA
# Save
# Repeat

import os
import random

basedir = "DNAVillage/"
MatingTreshold = 0.3        # how likely two individuals will mate

with open("movie-characters.txt", "r") as f:
    FirstNames = f.read()
    FirstNames = FirstNames.split("\n")
    
with open("Family-Names.txt", "r") as f:
    LastNames = f.read()
    LastNames = LastNames.split("\n")

def SelectDNA():
    # get the latest generation number
    generations = [directory.split("_")[1] for directory in os.listdir(basedir)]
    generations = [int(generations) for generations in generations]

    currentGeneration = max(generations)
    currentGeneration = str(currentGeneration)

    return currentGeneration
    
def CloneDNA(currentGeneration):
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

    # create directory
    os.mkdir(new_path_input)
    #os.mkdir(new_path_output)
    
    # copy the files in the old path to the new path
    
    # add a file to mark the input as "unmutated"
    with open(new_path_input + "unmutated", "w") as f:
        f.write(old_path_input)
        f.write(old_path_output)
    
    return (new_path_input, new_path_output, old_path_output)

def _EvaluateDNA(filename):
    # We evaluate using the match ranking and the tournament ranking,
    # with a higher priority for match ranking.
    matchRankStr      = "Yomi AI is match ranked "
    tournamentRankStr = "Yomi is tournament ranked "

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
        
    rank = float("%s.%s" % (matchRank, tournamentRank.zfill(2)))
    return rank

def _FindMates(path_input, old_path_output):
    Population = os.listdir(path_input)
    
    # filter out mutating mark
    Population = [Population for Population in Population if Population != "mutating"]
    
    # Add a fertility probabilty for each DNA. Todo: Higher ranking = higher fertility.
    Population = [[Population, _EvaluateDNA(old_path_output + Population)] for Population in Population]

    Population.sort(key = lambda a: a[1])

    AllPopulation = Population
    Population = []
    
    # filter in the top ranking individuals (30% + 1)
    topRankLen = int((len(AllPopulation) * 0.3) + 1)
    AlphaIndividuals = AllPopulation[0:topRankLen]
    Population.extend(AlphaIndividuals)
    
    # filter in the low ranking individuals (5% + 1)
    lowRankLen = int((len(AllPopulation) * 0.05) + 1)
    Population.extend(AllPopulation[-lowRankLen:])
    
    # filter in one random individual
    middleRandom = random.randint(topRankLen, len(AllPopulation) - lowRankLen)
    Population.append(AllPopulation[middleRandom])

    random.shuffle(Population)
    
    # Set the max population size. This can go up or down randomly
    maxPopulationSize = len(Population) * random.uniform(0.9, 1.1)
    maxPopulationSize = round(maxPopulationSize)
    
    # Set the minimum population size.
    maxPopulationSize = max(maxPopulationSize, 30)

    while maxPopulationSize > 0:
        maxPopulationSize -= 1
                    
        # Grab two random individual. Todo: Having higher fertility mate more likely
        Dominant = random.choice(Population)
        Mate     = random.choice(Population)
        
        # If we grabbed the same individual, just mutate it instead.
        if Dominant == Mate:
            newName, newDNA = _MutateDNA(Dominant)
            print("Same target")
            continue
        
        # Throw dice to decide if the two needs to mate
        if random.uniform(0, 1) < MatingTreshold: continue

        # If one of the partners has low fertility, grab a stranger to mate
        newName  = _MutateName(Dominant[0], Mate[0])
        newDNA   = _MateDNA(newName, Dominant, Mate)
        
        # write newDNA to file
        newFile = path_input + newName + ".txt"
        #with open(newFile) as f:
            #f.write(newDNA)
        print("mating", newFile)

        # Lower the fertility of both partners. If fertility goes below 2, remove from
        # population. If the population is exhausted, mutate the higher ranking individuals
        def LowerFertility(Individual, Rate):
            i = Population.index(Individual)
            Population[i][1] += Rate
            
            if Individual[1] >= 10:
                Population.remove(Individual)
        
        LowerFertility(Dominant, 3)
        LowerFertility(Mate, 2)
        
        if len(Population) < 2:
            break

    while maxPopulationSize > 0:
        # If we get here, it means that the population is exhausted but we have not yet
        # reached the max population size.
        maxPopulationSize -= 1
        Mutating = random.choice(AlphaIndividuals)

        newName, newDNA = _MutateDNA(Mutating)
        
        newFile = path_input + newName + ".txt"
        #with open(newFile) as f:
            #f.write(newDNA)
        print("mutanting", newFile)

def filterName(newLastName, newFirstName, newMiddleName):
    newLastName   = newLastName
    newFirstName  = newFirstName
    newMiddleName = newMiddleName
    
    # strip the symbols from the names (todo)
    #
    #
    #
    
    return newLastName + ", " + newFirstName + " " + newMiddleName    
    
def _StrangerName():
    # Return a randomly generated name
    newLastName   = random.choice(LastNames)
    newMiddleName = random.choice(LastNames)
    newFirstName  = random.choice(FirstNames)
    
    newName = filterName(newLastName, newFirstName, newMiddleName)
    return newName        

def _MutateName(DominantName, MateName):
    # DominantName is the name of the DNA with the most contribution.
    # MateName is the name of the DNA mated with.
    
    # Names taken from:
    #  http://www.outpost9.com/files/WordLists.html
    #  http://deron.meranda.us/data/
    
    newLastName   = DominantName.split(",")[0]
    newMiddleName = MateName.split(",")[0]
    newFirstName  = random.choice(FirstNames)
    
    newName = filterName(newLastName, newFirstName, newMiddleName)
    return newName

def _MateDNA(newName, Dominant, Mate):
    pass

def _MutateDNA(Original):
    newLastName   = Original[0].split(",")[0]
    newMiddleName = random.choice(LastNames)
    newFirstName  = random.choice(FirstNames)

    newName = filterName(newLastName, newFirstName, newMiddleName)

    newDNA = ""
    
    return newName, newDNA

def RunGA(path_input):
    # check for "unmutated" mark. If it doesn't exist, throw exception
    if not os.path.isfile(path_input + "unmutated"):
        raise Exception("%s do not have unmutated mark. Possible reason: MutateDNA was interrupted" % (path_input))
    
    # change "unmutated" mark to "mutating".
    os.rename(path_input + "unmutated", path_input + "mutating")
        
    _FindMates(path_input)
    
    # remove mark for "mutating".
    #os.unlink(path_input + "mutating")
    
def main():
    _FindMates("DNAVillage/input_0/", "DNAVillage/output_0/")

    #currentGeneration = SelectDNA()
    #path_input, path_output, new_path_output = CloneDNA(currentGeneration)
    #RunGA(path_input, new_path_output)
    
    #import trainer
    #trainer.main(path_input, path_output)
    
if __name__ == "__main__":
    main()
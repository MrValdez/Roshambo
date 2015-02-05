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
    os.mkdir(new_path_output)
    
    # copy the files in the old path to the new path
    
    # add a file to mark the input as "unmutated"
    with open(new_path_input + "unmutated", "w") as f:
        f.write(old_path_input)
        f.write(old_path_output)
    
    return (new_path_input, new_path_output)

def Mutate(path_input):
    # check for "unmutated" mark. If it doesn't exist, throw exception
    if not os.path.isfile(path_input + "unmutated"):
        raise Exception("%s do not have unmutated mark. Possible reason: MutateDNA was interrupted" % (path_input))
    
    # change "unmutated" mark to "mutating".
    os.rename(path_input + "unmutated", path_input + "mutating")
    
    def _MutateDNA():
        # Mutate DNA
        pass
    
    def _StrangerName():
        # Return a randomly generated name
        newLastName   = random.choice(LastNames)
        newMiddleName = random.choice(LastNames)
        newFirstName  = random.choice(FirstNames)
        
        newName = newLastName + ", " + newFirstName + " " + newMiddleName
        return newName        
    
    def _MutateName(DominantName, MateName)
        # DominantName is the name of the DNA with the most contribution.
        # MateName is the name of the DNA mated with.
        
        # Names taken from:
        #  http://www.outpost9.com/files/WordLists.html
        #  http://deron.meranda.us/data/
        
        newLastName   = DominantName.split(",")[0]
        newMiddleName = MateName.split(",")[0]
        newFirstName  = random.choice(FirstNames)
        
        newName = newLastName + ", " + newFirstName + " " + newMiddleName
        return newName
    
    # remove mark for "mutating".
    os.unlink(path_input + "mutating")
    
def main():
    currentGeneration = SelectDNA()
    path_input, path_output = CloneDNA(currentGeneration)
    Mutate(path_input)
    
    #import trainer
    #trainer.main(path_input, path_output)
    
if __name__ == "__main__":
    main()
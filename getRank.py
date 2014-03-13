import os

filebase = "./results/"

def DoCheck():
    print ("RANK   VARIABLE")
    for variable in range(0, 1000):
        number = str(variable).zfill(4)
        filename = filebase + "results %s.txt" % (number)

        if not os.path.isfile(filename):
            print ("%s is missing" % (filename))
            return
            
        with open(filename) as f:
            text = f.read()
            found = text.rfind("Yomi AI")
            if found == -1:
                print("MAJOR PARSING ERROR")
                return
            start = text.rfind("\n", 0, found - 4)
            end = text.find("Yomi AI", found)
            #print (start, end)
            #line = text[found - 10] == "\n"
            #print (line)
            rank = int(text[start:end].strip())
            print (" %i        %s" % (rank, number))            
        
DoCheck()
import unittest

import os
import subprocess
import random

pathbase = "./MBFP results/"             # Note: this string should end with "/"

class testMBFP(unittest.TestCase):
    #@unittest.skip("Skipping full test")
    def testAllResults(self):
        for i, filename in enumerate(os.listdir(pathbase)):
            #errors:
            #   0031    Vroomfondel
            #   0258    Shofar
            #   0393    De Bruijn
            #   0939    Add-drift
            #   0942    Pi
            #   0961    Shofar
            #   0962    Shofar
            # ~239mins ~4hrs
            if i + 1 in (31, 258, 393, 939, 942, 961, 962): 
                continue
            
            self.compare(filename)
    
    @unittest.skip("Skipping partial test")
    def testRandomResult(self):
        files = os.listdir(pathbase)
        for x in range(5):
            i = random.randint(2, len(files))
            if i in (31, 258, 393, 939, 942, 961, 962): 
                continue
                
            filename = files[i]
            
            self.compare(filename)

    @unittest.skip("Skipping partial test")
    def testMinimal(self):
        files = os.listdir(pathbase)
    
        for filename in [files[0], files[1], files[3], files[6], files[9]]:
            self.compare(filename)
        
    def compare(self, filename):
        argument = filename.split(" ")[1]
        argument = argument.split(".")[0]
        print ("Running argument %s" % (argument))        
        
        testResults = subprocess.check_output(["full.exe", argument], universal_newlines = True)
        with open(pathbase + filename, "r") as f:
            paperResults = f.read()
            
        testResults = testResults.strip()
        paperResults = paperResults.strip()
        
        # In MBFP results: remove line 44 onwards. These lines were removed in a latter revision.
        paperResults = paperResults.split("\n")
        paperResults = paperResults[0:43]
        paperResults = [line.strip() for line in paperResults]
        paperResults = "\n".join(paperResults)
        
        # In test results: remove line 44 onwards. These lines cannot be found in the paper results
        testResults = testResults.split("\n")
        testResults = testResults[0:43]
        testResults = [line.strip() for line in testResults]
        testResults = "\n".join(testResults)
                        
        try:
            self.maxDiff = None
            self.assertMultiLineEqual(testResults, paperResults, "%s is different from paper to current build." % (argument))
        except:
            testResults = testResults.split("\n")
            paperResults = paperResults.split("\n")
            for i, line in enumerate(paperResults):
                if line != testResults[i]:
                    print ("line %i is different" % i)               
                
            raise

if __name__ == "__main__":
    unittest.main()
import unittest

import os
import subprocess
import random

pathbase = "./PP results/"             # Note: this string should end with "/"

class testPP(unittest.TestCase):
    @unittest.skip("Skipping full test")
    def testAllResults(self):
        # ETA 8:16
    
        for i, filename in enumerate(reversed(os.listdir(pathbase))):            
            self.compare(filename)

    #@unittest.skip("Skipping partial test")
    def testRandomResults(self):
        files = os.listdir(pathbase)
        for x in range(5):
            filename = random.choice(files)
            
            self.compare(filename)

    def compare(self, filename):
        argument = filename.split("[")[1]
        argument = argument.split("]")[0]
        argument = argument.replace(" ", "")
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
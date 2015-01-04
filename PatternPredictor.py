import math
import rps

Debug = True
Debug = False

UseByteArray = True
UseByteArray = False

class PatternPredictor:
    def __init__(self, variant):        
        self.windowSize = None
        self.variant = variant
        self.reset()

    def reset(self):
        if UseByteArray:
            self.enemyHistory = bytearray()
        else:
            self.enemyHistory = ""
        self.init(self.variant)

        # DNA variable
        # targetDifference is the max number of counted tally where the AI becomes very confident of its answer
        # higher = weaker?
        #self.targetDifference = 5
        #self.targetDifference = 1
        self.targetDifference = 4
        
    def update(self):
        currentTurn = rps.getTurn()
        
        if currentTurn == 0:
            self.reset()
            return 0, 0         # play Rock with 0 confidence
            
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
        
        if UseByteArray:
            self.enemyHistory.append(enemyMoveLastTurn)
            #self.enemyHistory[currentTurn] = enemyMoveLastTurn
        else:
            self.enemyHistory += str(enemyMoveLastTurn)        
        
        
    def play(self):
        currentTurn = rps.getTurn()
        History = self.enemyHistory

        for SequenceLength in self.windowSize:
            if SequenceLength > currentTurn:
                # our window is bigger than the history size, so we ignore this window length
                continue

            prediction, confidence = self.CheckHistory(History, SequenceLength)
            if prediction != -1:
                return prediction, confidence
                
        # no Seq found.
        return 0, 0         # play Rock with 0 confidence

    def init(self, a):       
        if self.windowSize == None:
            if a == -1:
                # default windowSize
                a = [1, 2, 3, 4, 5]
                a.sort(reverse=True)
            else:
                a = str(a).split(",")
                a = [int(turn) for turn in a]
                a.sort(reverse=True)
                
            self.windowSize = a        

    def CheckHistory(self, History, SequenceLength):
        """return prediction, confidence"""

        Seq = History[-SequenceLength:]
        found = History.find(Seq, 0, -SequenceLength)
        if found == -1:
            return -1, -1

        # list how many times we see a predicted move
        tally = [0, 0, 0]      # [0] = rock, [1] = paper, [2] = scissor
        latestFoundSeq = -1
        while found != -1:
            # todo: very slow. optimize
            end = found + len(Seq)
            if UseByteArray:            
                move = History[end]
            else:
                move = History[end:end + 1]
            move = int(move)

            tally[move] += 1
            found = History.find(Seq, found + 1, -SequenceLength)
            
            # check if we get a tally that is greater than 150 compared to the other tallies.
            # this is an optimization to quickly end the loop.
            difference = 100
            if tally[0] >= tally[1] + difference and tally[0] >= tally[2] + difference:    
                break
            if tally[1] >= tally[0] + difference and tally[1] >= tally[2] + difference:    
                break
            if tally[2] >= tally[0] + difference and tally[2] >= tally[1] + difference:    
                break
     
        latestFoundSeq = History.rfind(Seq, 0)
        
        prediction, confidence = self.GetHighestTally(History, tally, SequenceLength, latestFoundSeq)

        if Debug:
            currentTurn = rps.getTurn()
            print ("History size:                  ", len(History))
            print ("Sequence to look for:          ", Seq)
            print ("Position of latest found Seq:  ", latestFoundSeq)
            print ("Predicted move:                ", prediction)
            print ("Confidence:                    ", confidence)
            input()

        return prediction, confidence
     
    def GetHighestTally(self, History, tally, SequenceLength, latestFoundSeq):                
        # check if we have a tie for maximum.
        maxCount = max(tally)
        numCount = tally.count(maxCount)

        if numCount == 1:
            # we don't have a tie for maximum. Get the highest move
            confidence = 1.0
            prediction = tally.index(maxCount)
            if Debug:
                print(":Highest tally found")
            return prediction, confidence                            
    
        # we have a tie.
        # let's see what move was played the most in the entire History
        moveCounts = [0, 0, 0]
        
        if UseByteArray:
            if tally[0] == maxCount: moveCounts[0] = History.count(0)
            if tally[1] == maxCount: moveCounts[1] = History.count(1)
            if tally[2] == maxCount: moveCounts[2] = History.count(2)
        else:
            if tally[0] == maxCount: moveCounts[0] = History.count("0")
            if tally[1] == maxCount: moveCounts[1] = History.count("1")
            if tally[2] == maxCount: moveCounts[2] = History.count("2")
        
        prediction = -1
        moveCountMax = max(moveCounts)
        moveCountNum = moveCounts.count(moveCountMax)
        if moveCountNum == 1:
            if Debug:
                print(":tally has ties. Found one move played the most")

            index = moveCounts.index(moveCountMax)
            prediction = index
            
            # targetDifference is the max number of counted tally where the AI becomes very confident of its answer
            targetDifference = self.targetDifference           
            
            # confidence = difference between the highest tally and how close it is to targetDifference
            confidence = (sum(moveCounts) - moveCountMax) / targetDifference
 #           confidence = 1
            
            if confidence >= 1: 
                confidence = 1
            elif confidence > 0 and targetDifference > 1:
                #confidence = (confidence * 0.5) + 0.5
                confidence = math.log(sum(moveCounts) - moveCountMax, targetDifference + 1)
                #print(confidence)
            else:
                confidence = 0
            
            confidence = (sum(moveCounts) - moveCountMax) / targetDifference
            
            
            confidence = latestFoundSeq / len(History)
            
            
            #confidence = math.log(sum(moveCounts) - moveCountMax, targetDifference + 1)
            #confidence = math.log(moveCounts[index], sum(moveCounts))
            #confidence = moveCounts[index] / sum(moveCounts)
#            sumOfOtherCounts = ((0 if index == 0 else moveCounts[0]) + 
#                                (0 if index == 1 else moveCounts[1]) +
#                                (0 if index == 2 else moveCounts[2]))
            #confidence = sumOfOtherCounts / moveCounts[index]
            #confidence = math.log(sumOfOtherCounts, moveCounts[index])
            #print(moveCounts)
            #print(moveCounts[index], sum(moveCounts))
            #print(((moveCounts[0] if index != 0 else 0) + (moveCounts[1] if index != 1 else 0) + (moveCounts[2] if index != 2  else 0)))
            #print (confidence)
            #confidence = 0.6           ##
            #confidence = 1
            
            if Debug:
                print ("target difference: ", targetDifference)
                print (moveCounts[prediction], sum(moveCounts), moveCountMax - sum(moveCounts), confidence)

#            if Debug and confidence > 1: 
#                print(confidence, sum(moveCounts) - moveCountMax)
#                input()
                
            if confidence > 1: confidence = 1
            return prediction, confidence

        # choose the move the was used last        
        if Debug:
            print(":Grabbing the move that was used last")
            
        latestR = latestP = latestS = 0             # position of latest move
        distToR = distToP = distToS = 0             # distance of move to end
        historySize = len(History)
        
        if tally[0] == maxCount:
            latestR = History.rfind("0")
            distToR = latestR / (historySize + 0)
            #distToR = math.log(latestR, historySize + 0)
        if tally[1] == maxCount:
            latestP = History.rfind("1")
            distToP = latestP / (historySize + 0)
            #distToP = math.log(latestP, historySize + 0)
        if tally[2] == maxCount:
            latestS = History.rfind("2")
            distToS = latestS / (historySize + 0)
            #distToS = math.log(latestS, historySize + 0)
            
        if latestR and (latestR > latestP or latestR > latestS):
            prediction = 0
            confidence = distToR - (distToP + distToS)
            confidence = distToR

        if latestP and (latestP > latestR or latestP > latestS):
            prediction = 1
            confidence = distToP - (distToR + distToS)
            confidence = distToP

        if latestS and (latestS > latestP or latestS > latestR):
            prediction = 2
            confidence = distToS - (distToP + distToR)
            confidence = distToS 

        #confidence = 1

        if prediction != -1:
            return prediction, confidence

        # if we still have a tie, choose between them using a random number
        sumCount = maxCount * numCount
        
        for i, count in enumerate(tally):
            if count == maxCount:
                tally[i] = count / sumCount
            else:
                tally[i] = 0
        
        random = rps.randomRange()
            
        for i, randomNumber in enumerate(tally):
            if random <= randomNumber:
                prediction = i
                break
            random -= randomNumber

        # our confidence is based on our random number
        #confidence = tally[prediction] - random 
        #confidence = 1 - random 
        #confidence = 1 - random 
        confidence = tally[prediction]
        
        if Debug:
            print (random, confidence)
            input()
                                
        return prediction, confidence
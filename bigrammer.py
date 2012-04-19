import sensplit
import copy

# Bigrammer corpus analyzing program
# by Logan Mitchell, Lindsay McNamara, and Colleen Darling (2011)
# 
# This program is designed to analyze the chance of bigrams (word pairs) appearing
# in small to medium sized corpora. It can also pull various statistics about the
# corpora, such as word frequency and likelyhood.

#Main functions --------------------------------------------------------------------------------------------------

#Checks for the probability of a given bigram in a known corpus
#(note: this assumes the bigram is for two words, not letters/syllables.)
# @corpusFilename   The filename of the corpus to load. Usually a txt file.
# @bigramword1      The first word of the bigram to check
# @bigramword2      The second word of the bigram to check
def getBigramChance(corpusFilename, bigramWord1, bigramWord2):

    bigramFrequencyList = makeBigramFreqList(corpusFilename) #get frequency of each bigram

    #quick check if we should continue - if file is not found, don't move on.
    if len(bigramFrequencyList) == 0:
        return
    
    tokenFrequencyList = makeWordFreqList(corpusFilename) #track frequency of each token

    #now that we have our lists, we do the statistical analysis part (as long as we have lists):
    if len(tokenFrequencyList) > 0 and len(bigramFrequencyList) > 0:

        try:
            #get bigram probability tables
            bigramProbabilityTable = getBigramProbTable(bigramFrequencyList, tokenFrequencyList)
        except MemoryError:
            print "Unable to get bigram chance; corpus size was too large. (Out of memory)"
            return

        #lastly check the user bigram pair.
        userBigram = bigramWord1.lower() + " " + bigramWord2.lower()

        #once we have the probilities, check if the input bigram exists in the table.    
        #if it exists, print the probability.
        if userBigram in bigramProbabilityTable:
            print "Probability of [" + userBigram + "]: " + str(bigramProbabilityTable[userBigram]*100) + "%"
        else:
            print "Probability of [" + userBigram + "]: 0% (Does not occur)"


#Predicts which word is likely to come next, using a given corpus as training data and a word to follow up on.
# @corpusFilename   The filename of the corpus to load. Usually a txt file.
# @bigramword1      The first word of the bigram to check
# @bigramword2      The second word of the bigram to check
# @predictWord      The word which will be checked for the most likely followup word, based on the corpus.
def predictNextWord(corpusFilename, predictWord):

    #display an error if they want to analyze a stop word.
    if isStopWord(predictWord):
        print "Cannot predict word following '" + predictWord + "'; '" + predictWord + "' is removed in corpus processing."
        return
    
    bigramFrequencyList = makeBigramFreqList(corpusFilename) #get frequency of each bigram
    tokenFrequencyList = makeWordFreqList(corpusFilename) #track frequency of each token

    if len(tokenFrequencyList) > 0 and len(bigramFrequencyList) > 0:

        try:
            #get bigram probability table
            bigramProbabilityTable = getBigramProbTable(bigramFrequencyList, tokenFrequencyList)
        except MemoryError:
            print "Unable to predict word; corpus size was too large. (Out of memory)"
            return

        #get the most likely word and print the details about it
        probPair = getLikelyNextWord(bigramProbabilityTable, predictWord)
            
        if len(probPair[0]) > 0:
            print "Next most likely word following '" + predictWord + "' is '" + probPair[0] + "'"
        else:
            #in cases where the word does not appear in the corpus at all...
            print "Unable to predict word based on chosen corpus."


#Print a likely sentence (minus function words) given a corpus, based on highest probabilities alone.
#finds a probable word, then makes a sentence out of it based on what is most likely to come next.
# @corpusFilename   The filename of the corpus to load. Usually a txt file.
def printLikelySen(corpusFilename):

    bigramFrequencyList = makeBigramFreqList(corpusFilename) #get frequency of each bigram
    tokenFrequencyList = makeWordFreqList(corpusFilename) #track frequency of each token

    if len(tokenFrequencyList) > 0 and len(bigramFrequencyList) > 0:
        
        #get probability tables
        try:
            wordProbabilityTable = getWordProbTable(tokenFrequencyList)
            bigramProbabilityTable = getBigramProbTable(bigramFrequencyList, tokenFrequencyList)
        except MemoryError:
            print "Unable to form sentence; corpus size was too large. (Out of memory)"
            return

        #find largest probability for a single word
        likelyWord = ''
        likelyProb = 0
        for word in wordProbabilityTable.keys():
            prob = wordProbabilityTable[word]
            if prob > likelyProb:
                likelyProb = prob
                likelyWord = word

        #now that we have the most likely word, make a sentence of 8 or less words using the bigram probabilities...

        senLength = 1
        sen = likelyWord
        prevSenWord = likelyWord
        while senLength < 8:
            nextWord = getLikelyNextWord(bigramProbabilityTable, prevSenWord)[0]
            if len(nextWord) == 0:
                sen += "."
                break
            sen +=  " " + nextWord
            prevSenWord = nextWord
            senLength += 1
            if senLength == 8:
                sen += "."

        print sen


#prints the bigram frequency list for a corpus
def printFreqList(filename):

    try:
        bigramFrequencyList = makeBigramFreqList(filename)
    except MemoryError:
            print "Unable to create frequency list; corpus size was too large. (Out of memory)"
            return

    for key in bigramFrequencyList.keys():
        print "Freq [" + key + "]:" + str(bigramFrequencyList[key])

#prints the bigram probability table for a corpus
def printBigramProbTable(filename):

    try:
        bigramFrequencyList = makeBigramFreqList(filename) #get frequency of each bigram
        tokenFrequencyList = makeWordFreqList(filename) #track frequency of each token
    except MemoryError:
        print "Unable to create frequency tables; corpus size was too large. (Out of memory)"
        return

    #now that we have our lists, we do the statistical analysis part (as long as we have lists):
    if len(tokenFrequencyList) > 0 and len(bigramFrequencyList) > 0:
             
        #get bigram probability tables
        try:
            bigramProbabilityTable = getBigramProbTable(bigramFrequencyList, tokenFrequencyList)
        except MemoryError:
            print "Unable to create bigram probability table; corpus size was too large. (Out of memory)"
            return

        total = 0
        for key in bigramProbabilityTable.keys():
            print "Probability [" + key + "]:" + str(bigramProbabilityTable[key])
            total += bigramProbabilityTable[key]

        print "Total: " + str(total)


#Helper Functions ----------------------------------------------------------------------------------------------

#Gets the most likely word to follow the predcitWord given the bigramProbabilityTable
#@return    Returns a list of two elements; the first is the likely next word, and the second is the probability of that word
def getLikelyNextWord(bigramProbabilityTable, predictWord):
    
    returnPair = [] #holds word and predictChance, to be returned.

    predictList = {}

    #cycle through all bigrams and check for ones that start with the input word
    for bigram in bigramProbabilityTable.keys():
        bigramParts = bigram.split()

        if bigramParts[0] == predictWord.lower():
            predictList[bigramParts[1]] = bigramProbabilityTable[bigram]

    if len(predictList) > 0:

        #find largest probability bigram of the ones we found, and note the values for it
        likelyWord = ''
        likelyProb = 0
        totalPredictChance = 0
        for word in predictList.keys():
            prob = predictList[word]
            totalPredictChance += prob
            if prob > likelyProb:
                likelyProb = prob
                likelyWord = word

        returnPair.append(likelyWord)
        #gives probability of this word out of all the recorded bigrams that have this word in it
        returnPair.append(int(float(likelyProb)*100))
        return returnPair
                
    else:
        #if we find nothing, return empty strings.
        return ["",""]

            
#Makes and returns the bigram probability table (dictionary) given a bigrm frequency list and a token frequency list
def getBigramProbTable(bigramFrequencyList, tokenFrequencyList):
    bigramProbabilityTable = {} #holds the final probability table
    
    #check the input lists exist:
    if len(tokenFrequencyList) > 0 and len(bigramFrequencyList) > 0:
             
        #copy all the bigrams into a new table that will report their probabilities.
        #causes memory issues; ideally we would just reuse bigramFrequencyList but no time.
        bigramProbabilityTable = copy.deepcopy(bigramFrequencyList)
        
        #Now calculate the probability of the bigram by using conditional probability
        #the two words are statistically independant, so the formula that follows describes the bigram probability:
        #P(word1 + word2) = count(bigram) / count(word1)
        for bigram in bigramProbabilityTable.keys():
            #get the two words that make up the bigram
            parts = bigram.split()
            #print "Freq [" + bigram + "] = " + str(bigramFrequencyList[bigram]) + "/" + str(tokenFrequencyList[parts[0]])
            bigramProbabilityTable[bigram] = float(bigramFrequencyList[bigram]) / tokenFrequencyList[parts[0]]

        #lastly, normalize
        total = 0
        for key in bigramProbabilityTable.keys():
            total += bigramProbabilityTable[key]

        for key in bigramProbabilityTable.keys():
            bigramProbabilityTable[key] = bigramProbabilityTable[key]/total

    return bigramProbabilityTable

#Returns the number of bigrams that have X frequency
def getNumBigramsOfFreq(bigramFrequencyList, x):

    occurances = 0
    for bigram in bigramFrequencyList.keys():
        #get how many times this bigram occurs
        countNum = bigramFrequencyList[bigram]
        if countNum == x:
            occurances += 1

    #print str(occurances) + " bigrams exist of frequency " + str(x)
    return occurances

#finds the maximum frequency out of all bigrams
def getMaxBigramFreq(bigramFrequencyList):
    maxFreq = 0
    for bigram in bigramFrequencyList.keys():
        #get how many times this bigram occurs
        countNum = bigramFrequencyList[bigram]
        if countNum > maxFreq:
            maxFreq = countNum

    return maxFreq

#returns an array with how many bigrams of each frequency occur
def queryBigramStats(bigramFrequencyList):
    statArray = []

    #first check the maximum count that is reached ('C' in Good-Turing discounting)
    maxFreq = getMaxBigramFreq(bigramFrequencyList)

    #go through 0-maxFreq and get how many of each frequency occurs. +1 due to 0-based index.
    for i in range(0,maxFreq+1):
        occurs = getNumBigramsOfFreq(bigramFrequencyList, i)
        statArray.append(occurs)

    #return array has C as index and value as Nc
    return statArray

#Gets the probability table for single words.
def getWordProbTable(tokenFrequencyList):
    #maybe do the same for single word probabilities if we need those to calculate bigram probabilities.
    wordProbabilityTable = copy.deepcopy(tokenFrequencyList)

    totalWords = 0
    #get total number of words (non-stop words)
    for word in tokenFrequencyList.keys():
        totalWords += tokenFrequencyList[word]

    #Get the probability of each word
    for word in wordProbabilityTable.keys():
        wordProbabilityTable[word] = float(tokenFrequencyList[word])/totalWords

    return wordProbabilityTable

#checks if a word exists in a text file full of stop words. returns True or False.
def isStopWord(word):
    wordFile = open("stopwords.txt")
    
    stopWords = wordFile.readlines()

    #check if any of the words in the file equal the input word
    for stopWord in stopWords:
        fixedWord = stopWord[:stopWord.find('\n')]
        #if they do, return true
        if fixedWord == word:
            return True
    
    #else...
    return False
    

#checks if a word has punctuation attached to it, and if so, returns the word stripped of punctuation.    
def removePunctuation(word):
    punctuationList = [".",",",":",";","!","?", "(", ")", "[", "]", '"', "'", "-"] #maybe more?
    updatedWord = word

    #check a piece of punctuation exists in the updatedWord, anywhere

    for punct in punctuationList:
        #if it does, remove the punctuation, set the new updatedWord, and start the search over
        #do this until no punctuation can be found in the word anymore
        while updatedWord.find(punct) >=0:
            pIndex = updatedWord.find(punct)
            updatedWord = updatedWord[:pIndex] + updatedWord[pIndex+1:]

    #lastly, return the updatedWord
    return updatedWord

#makes a bigram frequency list for a given corpus
def makeBigramFreqList(filename):
    bigramFrequencyList = {} #track freq of each bigram
    
    #split the corpus into sentences. (Due to assuming bigrams cannot cross sentence ends.)
    corpusSentences = sensplit.sen_splitter(filename)
    
    #quick check if we should continue - if file is not found, don't move on.
    if len(corpusSentences) == 0:
        return []

    wordFreqList = makeWordFreqList(filename)
    
    #make a combinatorial list of all bigram pairs first. (extras smoothed later)
    for word1 in wordFreqList:
        for word2 in wordFreqList:
            bigram = word1 + " " + word2
            bigramFrequencyList[bigram] = 0
    
    #for each sentence...
    for sen in corpusSentences:
        #Make tokens (words) from the sentence by splitting on whitespace.
        senTokens = sen.split()
        
        tokenPair = [] #keep track of our current bigram pair as we go through the sentence
        
        #for each 'word' in the current sentence...
        for token in senTokens:
            #ignore any stop words (function words, etc).
            #stop words will be found in stopwords.txt
            
            #first turn the token lowercase for easier comparison!
            token = token.lower()
           
            #remove punctuation if it exists in the current token.
            token = removePunctuation(token)
            
            #if not a stop word...
            if not isStopWord(token) and len(token.strip()) > 0:

                #add to our current tokenpair
                tokenPair.append(token)
                #if our tokenpair is now two words, add the pair to the bigramFreq list by
                #   combining the two words as the key; ex: "word1 word2" as a key, seperated by space
                #   Steps: check if pair exists already, if not add pair and set freq to 1 
                #      Ex.    bigramFrequencyList["word1 word2"] = 1
                #   If pair exists already, simply increment frequency for that pair by 1.
                if len(tokenPair) == 2:
                    pairKey = tokenPair[0] + ' ' + tokenPair[1]
                    if pairKey in bigramFrequencyList:
                        bigramFrequencyList[pairKey] += 1
                    else:
                        bigramFrequencyList[pairKey] = 1

                #if we put the tokenpair into the bigramFreq list, clear the current pair and start a new pair
                #   this pair will start with the current token as the first word.
                tokenPair = []
                tokenPair.append(token)


    #SMOOTHING TIME
    #use Good Turing discount formula to modify the frequency of the bigram table
    #Formula:
    # c* = (c+1) * NumBigramsOfFreq(C+1) / NumBigramsOfFreq(C)
        
    #NOTE: There is an inherent issue with Good Turing smoothing when numBigramsOfFreq(C+1) == 0
    #This becomes almost a non-issue with any regular sized corpus, but this smoothing will ruin
    #the frequencies by setting them to 0 if there are any interm frequency counts that are 0.
    #Moral: Don't use tiny data sets.
    #Source: http://www.ee.ucla.edu/~weichu/htkbook/node214_mn.html

    #Now, get some data we'll need for our formula...

    #get a list of all frequencies and occurances of those frequencies in the freq. list
    bigramStats = queryBigramStats(bigramFrequencyList)

    #make a new list to hold the new bigram frequencies we will replace the old ones with
    newBigramFrequencies = copy.deepcopy(bigramStats)

    #for each frequency... (Use -1 due to using c+1 and c being an index)
    for c in range(0,len(bigramStats)-1):
        #avoid division by 0 error
        if bigramStats[c] != 0:
            #Adjust the counts using the Good Turing Discount formula
            newBigramFrequencies[c] = float((c+1)*bigramStats[c+1])/bigramStats[c]
        else:
            newBigramFrequencies[c] = 0

    #Then replace the old frequency counts with the new frequency counts
    #The old frequency will be the index into the new array to get the updated count
    for bigram in bigramFrequencyList.keys():
        oldBigramFreq = bigramFrequencyList[bigram]
        bigramFrequencyList[bigram] = newBigramFrequencies[oldBigramFreq]

    return bigramFrequencyList

#makes a monogram (word) frequency list for a given corpus
def makeWordFreqList(filename):
    tokenFrequencyList = {} #track freq of each token
    
    #split the corpus into sentences.
    corpusSentences = sensplit.sen_splitter(filename)
    
    #for each sentence...
    for sen in corpusSentences:
        #Make tokens (words) from the sentence by splitting on whitespace.
        senTokens = sen.split()

        #for each 'word' in the current sentence...
        for token in senTokens:
            #ignore any stop words (function words, etc).
            #stop words will be found in stopwords.txt
            
            #first turn the token lowercase for easier comparison!
            token = token.lower()
           
            #remove punctuation if it exists in the current token.
            token = removePunctuation(token)
            
            #if not a stop word...
            if not isStopWord(token) and len(token.strip()) > 0:

                #add to the list
                if token in tokenFrequencyList:
                    tokenFrequencyList[token] += 1
                else:
                    tokenFrequencyList[token] = 1

    return tokenFrequencyList

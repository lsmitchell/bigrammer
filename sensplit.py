#From ps4 2.5 function II - Sentence splitter
# - Logan Mitchell

#returns a list of sentences made from the give corpus.
def sen_splitter(fileName):
    #try:
        #read the file data from the file
        try:
                senFile = open(fileName, "r")
        except:
                print "ERROR: File '" + fileName + "' not found."
                return []
                
        punctuationList = [".","!","?"]

        fileString = ""

        #read each line in the file and add it to the master string
        for line in senFile:
            fileString += line

        senFile.close()
        #split the string by spaces to get all the words
        wordList = fileString.split()

        #run through and make sentences from the word list.
        #we will determine a sentence to be terminated by anything in the
        #punctuation list.
        senList = []

        #keep a current sentence to be written to the sentence list.
        curSentence = ""
        for word in wordList:
            if word != "\n": #ignore newlines
                #check if this word ends in punctuation.
                finalChar = word[len(word)-1:]
                if finalChar == "." or finalChar == "?" or finalChar == "!":
                    #if our word ends in punctuation, it ends the sentence.
                    #add the sentence to the list and clear the current sentence.
                    curSentence += word + "\n"
                    senList.append(curSentence)
                    curSentence = ""
                else:
                    #if we don't end in punctuation, just continue adding to the current sentence.
                    curSentence += word + " "
                
        return senList
        
        

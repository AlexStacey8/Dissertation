#the following python script will act as a python module within my system
#the function are design to handle a individual tweets therefore must bes used as part of loop
#tokenisation prosses to split tweet into individual words
import re
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle

def cleanString(string):
    #firstly i will remove any urls from the tweet using a regular expression
    #given that there are no space in a url it is an easy task to remove then as when we come accross http we can remove the url completely
    cleanString = re.sub("http\S+","",string)
    #This is a regex that remove any non alphanumeric characters eg @
    #firstly i will remove ' because it can be used in indivual words such as don't
    cleanString2 = re.sub("['’]",'',cleanString)
    cleanString3 = re.sub('[^A-Za-z0-9]+',' ',cleanString2)
    return(cleanString3)

def tokenization(tweet):
    #splitting tweets into indivdual words
    tweetWords = tweet.split()
    #to make analysis simple i will make every word lower case
    tweetList = []
    for i in tweetWords:
        tweetList.append(i.lower())
    return(tweetList)
#function to remove stop words from the tweet
def stopWordRemover(tweet):
    cleanTweet = cleanString(tweet)
    tweetList = tokenization(cleanTweet)
    #opening stop word text file to read
    stopWords = open("StopWords.txt","r")
    for line in stopWords:
        for i in tweetList:
            if str(i) == line.strip():
                tweetList.remove(i)
            else:
                continue
    return(tweetList)

#function to determine a positive,negative and neutral word based of a bank of words within a text file
def getSentiment(tweetList):
    #creating counter variables to keep track of the number of positive or neagtive words
    positiveCounter = 0
    negativeCounter = 0
    #opening file of positive words
    postitiveWords = open("PositiveWords.txt","r")
    #opening file of negative words
    negativeWords = open("NegativeWords.txt","r")

    #firstly we will preform n-gram analysis of the tweet starting within trgrams, then filtering down to bigrams
    #we will stor all n-garms that hold sentiment within a list of lists so that when we
    #evaluate each word we can avoid ones within the ngrams we find

    #hold a list of trigarms (list of lists)
    ngrams = []
    trigrams = []
    if len(tweetList) < 3:
        pass
    else:
        for i in range(len(tweetList)):
            if i == (len(tweetList) - 2):
                break
            else:
                trigram = []
                trigram.append(tweetList[i])
                trigram.append(tweetList[i + 1])
                trigram.append(tweetList[i + 2])
                trigrams.append(trigram)
        # now I have the list of trigrams I can begin analysis
    for line in postitiveWords:
        for i in trigrams:
            # don't and didnt are used in trigarms to indicate the reverse of the following words such as "didnt really enjoy" or "dont really like"
            # sop if one of these words is the firt
            if ("dont" == i[0]) or ("don't" == i[0]) or ("didnt" == i[0]) or ("didn't" == i[0]) or ('no' == i[0]) or ('not' == i[0]) or ('wasnt' == i[0]):
                # check if last word is in the positive word bank if so we add to the negative counter
                if line.strip() == i[2]:
                    negativeCounter = negativeCounter + 1
                    ngrams.append(i)
                else:
                    continue
        else:
            continue

    # same code for checking trigarms for positive trigrams
    for line in negativeWords:
        for i in trigrams:
            # don't and didnt are used in trigarms to indicate the reverse of the following words such as "didnt really enjoy" or "dont really like"
            # so if one of these words is the firt
            if ("dont" == i[0]) or ("don't" == i[0]) or ("didnt" == i[0]) or ("didn't" == i[0]) or ('no' == i[0]) or ('not' == i[0]) or ('wasnt' == i[0]):
                # check if last word is in the positive word bank if so we add to the negative counter
                if line.strip() == i[2]:
                    positiveCounter = positiveCounter + 1
                    ngrams.append(i)
                else:
                    continue
        else:
            continue

    #no we will preform bigarm analysis
    #example include "don't like" (neagtive) and "not bad" (positive)

    # hold a list of bigarms (list of lists)
    bigrams = []
    if len(tweetList) < 2:
        pass
    else:
        for i in range(len(tweetList)):
            if i == (len(tweetList) - 1):
                break
            else:
                bigram = []
                bigram.append(tweetList[i])
                bigram.append(tweetList[i + 1])
                bigrams.append(bigram)
    #we have to use the seek method so the pointer is returned to the top line of the text files
    postitiveWords.seek(0)
    negativeWords.seek(0)
    # now I have the list of bigrams I can begin analysis
    for line in postitiveWords:
        for i in bigrams:
            # don't and didnt are used in bigarms to indicate the reverse of the following words such as "didntenjoy" or "dont like"
            # so if one of these words is the first
            if ("dont" == i[0]) or ("don't" == i[0]) or ("didnt" == i[0]) or ("didn't" == i[0]) or ('no' == i[0]) or ('not' == i[0]) or ('wasnt' == i[0]):
                # check if last word is in the positive word bank if so we add to the negative counter
                if line.strip() == i[1]:
                    negativeCounter = negativeCounter + 1
                    ngrams.append(i)
                else:
                    continue
        else:
            continue

    #same code for checking bigarms for positive bigrams
    for line in negativeWords:
        for i in bigrams:
            # don't and didnt are used in bigarms to indicate the reverse of the following words such as "didnt enjoy" or "dont like"
            # so if one of these words is the first
            if ("dont" == i[0]) or ("don't" == i[0]) or ("didnt" == i[0]) or ("didn't" == i[0]) or ('no' == i[0]) or ('not' == i[0]) or ('wasnt' == i[0]):
                # check if last word is in the positive word bank if so we add to the negative counter
                if line.strip() == i[1]:
                    positiveCounter = positiveCounter + 1
                    ngrams.append(i)
                else:
                    continue
        else:
            continue
    #now is the time to evaluate each indvidiual word within the tweet to determine its sentiment
    postitiveWords.seek(0)
    negativeWords.seek(0)
    #now i will check if a word is postivive and add it the the counter if ir isnt part of an exsisting ngram
    for line in postitiveWords:
        for i in tweetList:
            if (line.strip() == i) and not any((i in j ) for j in ngrams): #the any function looks to see if the word i is in any of the ngrams in the list
                positiveCounter = positiveCounter + 1
            else:
                continue
    # now to check the words to see if the are negative words using the same process
    for line in negativeWords:
        for i in tweetList:
            if (line.strip() == i) and not any((i in j ) for j in ngrams): #the any function looks to see if the word i is in any of the ngrams in the list
                negativeCounter = negativeCounter + 1
            else:
                continue
    if positiveCounter > negativeCounter:
        return("positive")
    elif positiveCounter < negativeCounter:
        return("negative")
    else:
        return("neutral")

def getClassifierSentiment(tweet):
    #this procces of creating a dictionary of the words within the tweet as this
    #is this form the classifier needs the tweet in
    #stopword removal process
    words = word_tokenize(tweet)
    usefulWords = [word for word in words if word not in stopwords.words("english")]
    tweetDict = dict([(word, True) for word in usefulWords])
    #now i will import my sentiment classifer created using a training set of data gained from
    #my twitter api
    f = open('sentimentClassifier.pickle', 'rb')
    classifier = pickle.load(f)
    sentiment = classifier.classify(tweetDict)
    return(sentiment)

def getFinalSentiment(tweet):
    #from my tests i found that my text clasification process was very good a classifiing negatives
    #correctly whereas the classifier i trained classifies to many tweets as negative
    #so to produce the most accurate sentiment analysis system I have combined both classifiers
    tweetList = stopWordRemover(tweet)
    #sentiment form the text classifier above
    textSentiment = getSentiment(tweetList)
    if textSentiment == "negative":
        return("negative")
    else:
        #now I will
        classifierSentiment = getClassifierSentiment(tweet)
        if classifierSentiment == "positive":
            return("positive")
        elif classifierSentiment == "neutral":
            return("neutral")
        #if the classifier returns negative then we will reasign the sentiment based on the text classifer
        else:
            tweetList = stopWordRemover(tweet)
            # sentiment form the text classifier above
            textSentiment2 = getSentiment(tweetList)
            if textSentiment2 == "positive":
                return("positive")
            elif textSentiment2 == "neutral":
                return("neutral")
            else:
                return("negative")


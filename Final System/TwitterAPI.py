
import datetime
import re
import tweepy
from tweepy import OAuthHandler
import TextClassifier
from textblob import TextBlob
#setting up database connection
import sqlite3 as sql
con = sql.connect("SentimentAnalysisSystem.db")
cur = con.cursor()
#creating a twitter API class that links my system to the API and contains methods for
class TwitterClient(object):
    def __init__(self):
        #construtor method, this method takes the access tokens and assigns them a vairable to be used in authentication
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'M1yUicHpgnOg5fq0TeGKclkCR'
        consumer_secret = '4U2CZyJz1u8GQqOmfqHoZyUj4VSRTWs0gSLL3aqSkYqqutb7tP'
        access_token = '518652599-usGZdxiMOzumVZBHLZVdXkxuJxRBXXgxlTv8Vc6i'
        access_token_secret = 'vaaE1cBEVoQAYaxMJoHBLfblquENobaZ4QAnLbzHMCi1n'
        #try and except for authentication
        try:
            #create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            #set access tokens
            self.auth.set_access_token(access_token, access_token_secret)
            #create tweepy API object taht will be used to gather tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    #method to get sentiment, employs methods from my text classifier module
    def getTweetSentiment(self, tweet):
        return(TextClassifier.getFinalSentiment(tweet))
        #for each query entered we want to create a sql table for it to store all the required information for my research

    def createDBTable(self, tableName):
        # Creating Table
        tableName1 = tableName.replace(" ", "")
        try:
            cur.execute("""SELECT COUNT (*) FROM """ + tableName1)
            if cur.fetchone()[0] >= 1:
                return(True)
        except:
            cur.execute('''CREATE TABLE ''' + tableName1 + '''(
                       tweetID INTEGER PRIMARY KEY AUTOINCREMENT,
                       tweet TEXT,
                       cleanTweet TEXT,
                       weekNo INT,
                       sentiment VARCHAR(255));''')

            con.commit()
            return(False)

    def populateDB(self,tableName,tweets,weekNo):
        for tweetDict in tweets:
            tweet = tweetDict.get("tweet")
            sentimentOfTweet = tweetDict.get("sentiment")
            cleanTweet = str(TextClassifier.stopWordRemover(tweet))
            cur.execute("""SELECT COUNT(*) FROM """ + tableName + """ WHERE tweet=?""",(tweet,))
            if cur.fetchone()[0] >= 1:
                continue
            else:
                cur.execute("""INSERT INTO """ + tableName + """ (tweet,cleanTweet,sentiment,weekNo) VALUES (?,?,?,?)""", (tweet,cleanTweet,sentimentOfTweet,weekNo,))

        con.commit()

    def getTweets(self, query):
        #empty list to store gathered tweets, individual they will be stored as ditionaries
        #keys will be tweet and sentiment
        tweets = []
        #try and except to search api for the tweets

        try:
            #call twitter api to gather tweets based on query input
            api = self.api
            for tweet in tweepy.Cursor(api.search, q=str(query), lang='en').items(500):
                #empty dictionary to store tweet and sentiment of a tweet
                returnedTweet = {}
                #saving text of tweet
                returnedTweet['tweet'] = tweet.text
                #saving sentiment of tweet
                returnedTweet['sentiment'] = self.getTweetSentiment(tweet.text)
                #appending the returned tweet to thetweets list
                #twitter has retweets which is simple a copy of the original reposted so we need to skip past these retweets
                if tweet.retweet_count > 0:
                    #if tweet has retweets only add it to the returned tweet list once
                    if returnedTweet not in tweets:
                        tweets.append(returnedTweet)
                    else:
                        continue
                else:
                    tweets.append(returnedTweet)
            return(tweets)
        except tweepy.TweepError as error:
            #print error (if any)
            print("Error : " + str(error))
    def getWeekNO(self,rDate):
        # now to determine what week in the critical period
        currentDate = datetime.datetime.now()
        releaseDate1 = datetime.datetime.strptime(rDate,"%Y-%m-%d")
        week1StartDate = (releaseDate1 - datetime.timedelta(days=7))
        week2StartDate = releaseDate1 + datetime.timedelta(days=1)
        week2EndDate = week2StartDate + datetime.timedelta(days=6)
        week3StartDate = week2StartDate + datetime.timedelta(days=7)
        week3EndDate = week3StartDate + datetime.timedelta(days=6)
        weekNo = 0
        if week1StartDate <= currentDate <= releaseDate1:
            weekNo = 1
        elif week2StartDate <= currentDate <= week2EndDate:
            weekNo = 2
        elif week3StartDate <= currentDate <= week3EndDate:
            weekNo = 3
        else:
            weekNo = 0
        return(weekNo)

    #simple count functions to return the total number of positive/negative/neutral tweets returned
    def countPostiveTweets(self,tableName,weekNo):
        sentiment = 'positive'
        cur.execute('''SELECT COUNT(sentiment) FROM ''' + tableName + ''' WHERE sentiment = ? AND weekNo = ?''',(sentiment,weekNo,))
        return(cur.fetchone()[0])

    def countNegativeTweets(self, tableName,weekNo):
        sentiment = 'negative'
        cur.execute('''SELECT COUNT(sentiment) FROM ''' + tableName + ''' WHERE sentiment = ? AND weekNo = ?''', (sentiment,weekNo,))
        return (cur.fetchone()[0])

    def countNeutralTweets(self, tableName,weekNo):
        sentiment = 'neutral'
        cur.execute('''SELECT COUNT(sentiment) FROM ''' + tableName + ''' WHERE sentiment = ? AND weekNo = ?''', (sentiment,weekNo,))
        return (cur.fetchone()[0])

    def totalNumberOfTweets(self, tableName):
        cur.execute('''SELECT COUNT (*) FROM ''' + tableName)
        return(cur.fetchone()[0])

    def populateReultsTable(self,tableName,weekNo):
        posTweets = int(self.countPostiveTweets(tableName,weekNo))
        negTweets = int(self.countNegativeTweets(tableName,weekNo))
        neuTweets = int(self.countNeutralTweets(tableName,weekNo))
        cur.execute("""SELECT COUNT (*) FROM AnalysisResults WHERE FilmTitle = ?""",(tableName,))
        #if result in analysis table then we add polarity and subjectivitey to the second slot
        if int(cur.fetchone()[0]) >= 1:
            polarity = float(posTweets/negTweets)
            subjectivity = float((posTweets + negTweets)/neuTweets)
            cur.execute("""UPDATE AnalysisResults SET Polarity2 = ?, Subjectivity2 = ? WHERE filmTitle = ?""",(polarity,subjectivity,tableName,))
            con.commit()
        else:
            polarity = float(posTweets / negTweets)
            subjectivity = float((posTweets + negTweets)/neuTweets)
            cur.execute("""INSERT INTO AnalysisResults (FilmTitle,Polarity,Subjectivity) VALUES (?,?,?)""",(tableName,polarity,subjectivity,))
            con.commit()

        #add option if both are full make pol2 = pol1 etc.
def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    print(api.getTweetSentiment("hello"))
    #calling function to get tweets
    query = str(input("Enter A Movie Title>> "))
    query2 = str(query.replace(" ", ""))
    #releaseDate = str(input("Enter the release date yyyy-mm-dd >> "))
    api.createDBTable(query2)
    tweets = api.getTweets(query2)
    print(tweets)
    api.populateDB(query2,tweets)
    print("----------{Results}----------")
    print('Number of postive tweets: ' +  str(api.countPostiveTweets(query2)))
    print('Number of neutral tweets: ' + str(api.countNeutralTweets(query2)))
    print('Number of negative tweets: ' + str(api.countNegativeTweets(query2)))

    percentageOfPositiveTweets = float((api.countPostiveTweets(query2)/api.totalNumberOfTweets(query2))*100)
    percentageOfNeutralTweets = float((api.countNeutralTweets(query2)/api.totalNumberOfTweets(query2))*100)
    percentageOfNegativeTweets = float((api.countNegativeTweets(query2)/api.totalNumberOfTweets(query2))*100)

    print("Percentage of Postive tweets: " + str(round(percentageOfPositiveTweets,2)) + '%')
    print("Percentage of Neutral tweets: " + str(round(percentageOfNeutralTweets, 2)) + '%')
    print("Percentage of Negative tweets: " + str(round(percentageOfNegativeTweets,2))+'%')




if __name__ == "__main__":
    #calling main function
    main()

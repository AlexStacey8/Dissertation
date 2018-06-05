#importing modules for the final system
from tkinter import *
import tkinter.ttk as ttk
#setting up database connection
import sqlite3 as sql
import datetime
import re
import tweepy
from tweepy import OAuthHandler
import TextClassifier
import TwitterAPI
con = sql.connect("SentimentAnalysisSystem.db")
cur = con.cursor()
#gui class that will contain all the methods that the gui will use
#such as creating an destroying new windows
class GUI:
    def __init__(self,root):
        self.root = root
        root.configure(background='#c0deed')
        root.title("Twitter Sentiment Analysis For Films")
        #for this gui i will use the tkinter grid method to arrange the elements
        titleLabel = Label(self.root,text="Twitter Sentiment Analysis System",borderwidth=2, relief="ridge",bg="#ffffff",font=("arial", 18))
        titleLabel.grid(row=0,padx=(10,10),pady=(10,10))
        infoLabel = Label(self.root,text="This system aims to produce a prediction about a given movies future success \n" +
                                         "based on the sentiment of the tweets the public have tweeted about the film",font=("arial", 12),bg='#c0deed')
        infoLabel.grid(row=1,padx=(10,10),pady=(10,10))
        startButton = Button(self.root,text="Launch",bg="#0084b4",font=("arial", 18),command=self.inputPage)
        startButton.grid(row=2,padx=(10,10),pady=(10,10))
        #the gui in the init function will be a simple home screen explaining the system

    #function that opens and runs the data gathering gui
    #this window will take user input and then will get the data from there
    def inputPage(self):
        #destory previous window
        self.root.destroy()
        #create class
        infoPage = Tk()
        infoPageGui = infoPageGUI(infoPage)
        infoPage.mainloop()
class infoPageGUI:
    def __init__(self,root):
        self.root = root
        root.configure(background='#c0deed')
        root.title("Twitter Sentiment Analysis For Films")
        self.infoLabel = Label(self.root,text="Enter Film Details",font=("arial", 14), bg='#c0deed')
        self.infoLabel.grid(row=0, padx=(10, 10), pady=(10, 10))
        #widgets to enter film title and release date
        self.filmLabel = Label(self.root,text="Film Title",font=("arial", 12), bg='#c0deed')
        self.filmLabel.grid(row=1, padx=(10,0), pady=(10, 10))
        self.filmEntry = Entry(self.root)
        self.filmEntry.grid(row=1,column=1, padx=(0, 10), pady=(10, 10))
        self.rdLabel = Label(self.root,text="Release Date",font=("arial", 12), bg='#c0deed')
        self.rdLabel.grid(row=2, padx=(10,0), pady=(10, 10))
        self.rdEntry = Entry(self.root)
        self.rdEntry.grid(row=2, column=1, padx=(0, 10), pady=(10, 10))
        self.rdEntry.insert(0, 'YYYY-MM-DD')
        #button to search
        self.searchButton = Button(self.root, text="Search", bg="#0084b4", font=("arial", 18),command=self.searchTwitterAPI)
        self.searchButton.grid(row=3,column=1, padx=(10, 10), pady=(10, 10))

        self.filmTitle = self.filmEntry.get()
    def goToResults(self):
        # destory previous window
        self.root.destroy()
        # create class
        results = Tk()
        resultsGui = resultsPageGUI(results)
        results.mainloop()

    def searchTwitterAPI(self):
        query = str(self.filmEntry.get())
        releaseDate = str(self.rdEntry.get())
        dbTableName = str(query.replace(" ", ""))
        filmTitleFile = open("filmTitle.txt", "w")
        filmTitleFile.write(str(dbTableName)+"\n")
        filmTitleFile.write(releaseDate)
        filmTitleFile.close()
        api = TwitterAPI.TwitterClient()
        weekNo = api.getWeekNO(releaseDate)
        tableExists = api.createDBTable(dbTableName)
        if tableExists:
            #check if there are tweets with the same week number if there are
            #and the weekNO is differenet then we search for tweets and add them
            #else we just continue
            cur.execute("""SELECT COUNT(*) FROM """ + str(dbTableName) + """ WHERE weekNo=?""",(weekNo,))
            if cur.fetchone()[0] >= 1:
                self.goToResults()
            else:
                tweets = api.getTweets(query)
                api.populateDB(dbTableName, tweets, weekNo)
                api.populateReultsTable(dbTableName, weekNo)
                self.goToResults()
        else:
            tweets = api.getTweets(query)
            #now we will see if the table is in the database and if it is we will
            #then check if the data we are adding is new if it is the it will be added to the db
            api.createDBTable(dbTableName)
            api.populateDB(dbTableName,tweets,weekNo)
            api.populateReultsTable(dbTableName,weekNo)
            self.goToResults()

class resultsPageGUI:
    def __init__(self,root):
        self.root = root
        root.configure(background='#c0deed')
        root.title("Twitter Sentiment Analysis For Films")
        #label for the title of the page
        self.resultsLabel = Label(self.root, text="Results", font=("arial", 18), bg='#c0deed')
        self.resultsLabel.grid(row=0, padx=(10, 10), pady=(10, 10))
        #polarity labekl and result label
        self.polarityLabel = Label(self.root,text="Polarity = ",font=("arial", 12), bg='#c0deed')
        self.polarityLabel.grid(row=1, padx=(10,0), pady=(10, 10))
        self.polarityResult = Label(self.root,text=" 0",font=("arial", 12), bg='#c0deed')
        self.polarityResult.grid(row=1,column=1, padx=(0,10),pady=(10, 10))
        #subjectivity label and result
        self.subjectivityLabel = Label(self.root, text="Subjectivity = ", font=("arial", 12), bg='#c0deed')
        self.subjectivityLabel.grid(row=2, padx=(10, 0), pady=(10, 10))
        self.subjectivityResult = Label(self.root, text=" 0", font=("arial", 12), bg='#c0deed')
        self.subjectivityResult.grid(row=2, column=1, padx=(0, 10), pady=(10, 10))
        #week in critial period label and result
        self.weekLabel = Label(self.root, text="Week in \n Critical Period ", font=("arial", 12), bg='#c0deed')
        self.weekLabel.grid(row=3, padx=(10, 0), pady=(10, 10))
        self.weekResult = Label(self.root, text=" 0", font=("arial", 12), bg='#c0deed')
        self.weekResult.grid(row=3, column=1, padx=(0, 10), pady=(10, 10))
        #change in polarity and subjectivity labels and results
        self.polarityCLabel = Label(self.root, text=" Change in \n Polarity = ", font=("arial", 12), bg='#c0deed')
        self.polarityCLabel.grid(row=4, padx=(10, 0), pady=(10, 10))
        self.polarityCResult = Label(self.root, text=" 0", font=("arial", 12), bg='#c0deed')
        self.polarityCResult.grid(row=4, column=1, padx=(0, 10), pady=(10, 10))
        self.subjectivityCLabel = Label(self.root, text="Change in \n Subjectivity = ", font=("arial", 12), bg='#c0deed')
        self.subjectivityCLabel.grid(row=5, padx=(10, 0), pady=(10, 10))
        self.subjectivityCResult = Label(self.root, text=" 0", font=("arial", 12), bg='#c0deed')
        self.subjectivityCResult.grid(row=5, column=1, padx=(0, 10), pady=(10, 10))
        #prediction label and result
        self.prediction = Label(self.root, text="Prediction = ", font=("arial", 12), bg='#c0deed')
        self.prediction.grid(row=6, padx=(10, 0), pady=(10, 10))
        self.predictionResult = Label(self.root, text="Prediction \n result", font=("arial", 12), bg='#c0deed')
        self.predictionResult.grid(row=6, column=1, padx=(0, 10), pady=(10, 10))
        #view tweets button
        #this button will take the user to a new page whihc will list all the tweets
        self.viewTweetsButton = Button(self.root, text="View Tweets", bg="#0084b4", font=("arial", 14),command=self.viewTweets)
        self.viewTweetsButton.grid(row=7, padx=(10, 10), pady=(10, 10))
        #search again button will simple take the user back to the search page
        self.search = Button(self.root,text="Search",bg="#0084b4",font=("arial", 14),command=self.inputPage)
        self.search.grid(row=7,column=1, padx=(10, 10), pady=(10, 10))
        #help button will simple be a page of text to tell the user what everything means
        #open a text film of info if possible
        self.help = Button(self.root,text="?",bg="#0084b4",font=("arial", 14),command=self.openInfoTxt)
        self.help.grid(row=7,column=2, padx=(10, 10), pady=(10, 10))
        self.populateResultsPage()
        self.getPrediction()
    def openInfoTxt(self):
        import os
        os.startfile("info.txt")
    def populateResultsPage(self):
        file = open("filmTitle.txt","r")
        lines = file.readlines()
        rdate = lines[1].strip()
        tableName = lines[0].strip()
        api = TwitterAPI.TwitterClient()
        weekNO = api.getWeekNO(rdate)
        polarity = api.countPostiveTweets(tableName,weekNO)/api.countNegativeTweets(tableName,weekNO)
        subjectivity = (api.countPostiveTweets(tableName,weekNO)+api.countNegativeTweets(tableName,weekNO))/api.countNeutralTweets(tableName,weekNO)
        self.polarityResult.config(text=str(polarity))
        self.subjectivityResult.config(text=str(subjectivity))
        self.weekResult.config(text=str(weekNO))
        #now to get the chnage in polarity and subjectivity
        try:
            polarityChange = polarity - (api.countPostiveTweets(tableName,(weekNO - 1))/api.countNegativeTweets(tableName,(weekNO - 1)))
            subjectivityChange = subjectivity - ((api.countPostiveTweets(tableName,(weekNO - 1)) + api.countNegativeTweets(tableName,(weekNO - 1)))/api.countNeutralTweets(tableName,(weekNO-1)))
            #now i will set all the labels to the new values
            self.polarityCResult.config(text=str(polarityChange))
            self.subjectivityCResult.config(text=str(subjectivityChange))
        except ZeroDivisionError:
            self.polarityCResult.config(text="N/A")
            self.subjectivityCResult.config(text="N/A")

    def getPrediction(self):
         #get prediction of fillms succuess based on a five tier system i created and refined through data mining
         polarity = float(self.polarityResult['text'])
         subjectivity = float(self.subjectivityResult['text'])
         polarityChange = self.polarityCResult['text']
         subjectivityChange = self.subjectivityCResult['text']
         #now i will create a decision tree of if statments to determine prediction
         # get film title
         f = open("filmTitle.txt", "r")
         f.seek(0)
         fileList = f.readlines()
         filmTitle = fileList[0]
         film = str(filmTitle.strip())
         if polarityChange == "N/A":
             polarityChange = 0
             if polarity > 4:
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", ("Very Good", film,))
             elif polarity > 3.5 and polarity <= 4:
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", ("Good", film,))
             elif polarity < 3.5 and polarity >= 2:
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", ("Okay", film,))
             elif polarity < 2 and polarity >= 1:
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", ("Bad", film,))
             elif polarity < 1:
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", ("Very Bad", film,))
         else:
             polarityChange = float(polarityChange)

         if subjectivityChange == "N/A":
             subjectivityChange = 0
         else:
             subjectivityChange = float(subjectivityChange)

         #now we will see if there is a change in polarity and subjectivity
         predictions = ["Very Bad","Bad","Okay","Good","Very Good"]
         if float(polarityChange) > 2:
             cur.execute("""SELECT Prediction FROM AnalysisResults WHERE FilmTitle=?""",(film,))
             currentPrediction = cur.fetchone()[0]
             index = predictions.index(str(currentPrediction))
             #so we get the prediction form the database and see where it is in the list and see if we can increase it
             if index <= 3:
                index = index + 1
                newPrediction = predictions[index]
                cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", (newPrediction, film,))
             else:
                 pass
         elif float(polarityChange) < -2:
             cur.execute("""SELECT Prediction FROM AnalysisResults WHERE FilmTitle=?""", (film,))
             currentPrediction = cur.fetchone()[0]
             index = predictions.index(str(currentPrediction))
             # so we get the prediction form the database and see where it is in the list and see if we can increase it
             if index >= 1:
                 index = index - 1
                 newPrediction = predictions[index]
                 cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""", (newPrediction, film,))
             else:
                 pass
         else:
             #check if there is a change in subjectivity
             #and polarity increases it mean people are sharing more positive opinions
             if float(subjectivityChange) > 1 and float(polarityChange) > 0:
                 cur.execute("""SELECT Prediction FROM AnalysisResults WHERE FilmTitle=?""", (film,))
                 currentPrediction = cur.fetchone()[0]
                 index = predictions.index(str(currentPrediction))
                 # so we get the prediction form the database and see where it is in the list and see if we can increase it
                 if index <= 3:
                     index = index + 1
                     newPrediction = predictions[index]
                     cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""",(newPrediction, film,))
                 else:
                     pass
             #same as before however if polarity decreases that implies people are sharing more negitive opions
             if float(subjectivityChange) > 1 and float(polarityChange) < 0:
                 cur.execute("""SELECT Prediction FROM AnalysisResults WHERE FilmTitle=?""", (film,))
                 currentPrediction = cur.fetchone()[0]
                 index = predictions.index(str(currentPrediction))
                 # so we get the prediction form the database and see where it is in the list and see if we can increase it
                 if index >= 1:
                     index = index - 1
                     newPrediction = predictions[index]
                     cur.execute("""UPDATE AnalysisResults SET Prediction=? WHERE FilmTitle=?""",(newPrediction, film,))
                 else:
                     pass

         cur.execute("""SELECT Prediction FROM AnalysisResults WHERE FilmTitle=?""",(film,))
         prediction = cur.fetchone()[0]
         self.predictionResult.config(text=str(prediction))
         con.commit()

    def inputPage(self):
        #destory previous window
        self.root.destroy()
        #create class
        infoPage = Tk()
        infoPageGui = infoPageGUI(infoPage)
        infoPage.mainloop()

    def viewTweets(self):
        # destory previous window
        self.root.destroy()
        # create class
        tweetsPage = Tk()
        infoPageGui = viewTweetsPage(tweetsPage)
        tweetsPage.mainloop()


class viewTweetsPage():
    def __init__(self,root):
        self.root = root
        root.configure(background='#c0deed')
        root.title("Twitter Sentiment Analysis For Films")
        #label for the title of the page
        titleLabel = Label(self.root, text="Tweets", font=("arial", 18), bg='#c0deed')
        titleLabel.grid(row=0, padx=(10, 10), pady=(10, 10))
        #total number of tweets label
        self.volumeOfTweetsLabel = Label(self.root, text="Total Number Of Tweets: 0 ", font=("arial", 12), bg='#c0deed')
        self.volumeOfTweetsLabel.grid(row=1, padx=(10,0), pady=(10, 10))
        #setting up treeview to be populated by database data
        # Treeview that will display the film tweets Table
        self.tweetsTreeview = ttk.Treeview(self.root)
        # setting up Treeview columns
        self.tweetsTreeview["columns"] = ("one", "two", "three")
        # Setting up column widths
        self.tweetsTreeview.column("#0", width=0)
        self.tweetsTreeview.column("one", width=50)
        self.tweetsTreeview.column("two", width=400)
        self.tweetsTreeview.column("three", width=100)
        # asigning columns headings
        self.tweetsTreeview.heading("#0", text="")
        self.tweetsTreeview.heading("one", text="TweetID")
        self.tweetsTreeview.heading("two", text="Tweets")
        self.tweetsTreeview.heading("three", text="Sentiment")
        # packing tree into frame
        self.tweetsTreeview.grid(row=2,column=0, padx=(10,0), pady=(10, 10))
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(1, weight=1)
        #button that opens widow that allows the user to change the sentiment given that the system is 100% accurate
        changeSentiment = Button(self.root, text="Change Sentiment", bg="#0084b4", font=("arial", 14),command=self.changeSentiment)
        changeSentiment.grid(row=2,column=1,padx=(10,10), pady=(10, 10))
        #back button to go back to results
        backButton = Button(self.root, text="Back To Results", bg="#0084b4", font=("arial", 14),command=self.goToResults)
        backButton.grid(row=3,column=1,padx=(10, 10), pady=(10, 10))
        self.getTreeviewData()

    def goToResults(self):
        # destory previous window
        self.root.destroy()
        # create class
        results = Tk()
        resultsGui = resultsPageGUI(results)
        results.mainloop()
    def getTreeviewData(self):
        #method to get all the data for the tree view
        #getting the data from table and putting it into lists
        #getting filmIDs
        f = open("filmTitle.txt","r")
        f.seek(0)
        fileList = f.readlines()
        filmTitle = fileList[0]
        film = str(filmTitle.strip())
        tweetIDList = []
        cur.execute("""SELECT tweetID FROM """ + film)
        for i in cur.fetchall():
            tweetIDList.append(i[0])
        cur.execute("""SELECT tweet FROM """ + film)
        tweetList = []
        for i in cur.fetchall():
            tweetList.append(TextClassifier.cleanString(i[0]))
        cur.execute("""SELECT sentiment FROM """ + film)
        sentimentList = []
        for i in cur.fetchall():
            sentimentList.append(i[0])
        x = 0
        for i in tweetIDList:
            self.tweetID = i
            self.tweet = tweetList[x]
            self.sentiment = sentimentList[x]
            x = x + 1
            self.tweetsTreeview.insert("", i, text=i, values=(self.tweetID, self.tweet, self.sentiment))  # inserting attribiutes

        cur.execute("""SELECT COUNT(*) FROM """ + str(film))
        self.volumeOfTweetsLabel.config(text="Total Number Of Tweets: " + str(cur.fetchone()[0]) )
    def changeSentiment(self):
        #method to change the sentiment values of the tweet given tweet ID
        window = Toplevel()
        window.configure(background='#c0deed')
        window.title("Twitter Sentiment Analysis For Films")
        self.tweetIDLabel = Label(window, text="Tweet ID", font=("arial", 12), bg='#c0deed')
        self.tweetIDLabel.grid(row=0, padx=(10, 0), pady=(10, 10))
        self.tweetIDEntry = Entry(window)
        self.tweetIDEntry.grid(row=0, column=1, padx=(0, 10), pady=(10, 10))
        self.newSentimentLabel = Label(window, text="New Sentiment", font=("arial", 12), bg='#c0deed')
        self.newSentimentLabel.grid(row=1,padx=(10,0), pady=(10, 10))
        self.newSentimentEntry = Entry(window)
        self.newSentimentEntry.grid(row=1, column=1, padx=(0,10), pady=(10, 10))
        #button to update db table
        updateButton = Button(window, text="Update Sentiment", bg="#0084b4", font=("arial", 14),command=self.updateSentiment)
        updateButton.grid(row=2, column=1, padx=(10, 10), pady=(10, 10))
    def updateSentiment(self):
        tweetID = int(self.tweetIDEntry.get())
        sentiment = str(self.newSentimentEntry.get())
        f = open("filmTitle.txt", "r")
        f.seek(0)
        fileList = f.readlines()
        filmTitle = fileList[0]
        film = str(filmTitle.strip())
        cur.execute("""UPDATE """ + film + """ SET sentiment=? WHERE tweetID=?""",(sentiment,tweetID))
        con.commit()


root = Tk()
gui = GUI(root)
root.mainloop()
import sqlite3 as sql
con = sql.connect("SentimentAnalysisSystem.db")
cur = con.cursor()

    
film = "Rampage"
print("""SELECT tweetID FROM """ + film)



cur.execute("""SELECT COUNT(*) FROM """ + film)
print(cur.fetchone()[0])

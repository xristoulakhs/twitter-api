import csv
import tweepy
import os
import time
import pandas as pd
import igraph
import matplotlib as plt

#enviroment variables for authentication
os.environ['BEARER'] = 'AAAAAAAAAAAAAAAAAAAAAMWXjgEAAAAAL7iVTqpK9cGfEzi1BPBdWCw0ui4%3DNhqGho6qEnrPi1XytDmkTc580PH3rUtQXw4ah3CdwoqoBNJtES'
os.environ['APIKEY'] = 'wEI3ZtQBfg3GKMeSQcEBfrMQb'
os.environ['APISECRET'] = 'ysmFgZHOJt3Sp4VBABfPIjuf3xKAb7KHMY0SmxKopLMS6iDkHO'
os.environ['ACCTOKEN'] = '1594357091422044161-B3hDEhItin4oY9tbb4D2iBl1PE8Sgi'
os.environ['ACCSECRET'] = 'bQwQlCkRlRzaAXdp9OPrSFwTDiw4QH2ZkcWbicbXRTlKs'

api = None

def authentication():
    auth = tweepy.OAuthHandler(os.getenv('APIKEY'),os.getenv('APISECRET'))
    auth.set_access_token(os.getenv('ACCTOKEN'),os.getenv('ACCSECRET'))
    #we initalize the api here
    global api
    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Successful authentication")
    except:
        print("Authentication failed")

#extract data
#words = the hashtag we will use
#date = the date which the tweets we want to see
def initData(words,date,tweetNum):
    #create dataframe
    data = pd.DataFrame(columns=['user_id',
                                 'username',
                                 'location',
                                 'following',
                                 'followers',
                                 'totaltweets',
                                 'retweetcount',
                                 'text',
                                 'hashtags'])

    #.Cursor() for search
    #.items(num) to define the number of the returned tweets
    tweets = tweepy.Cursor(api.search_tweets,
                           q = words,
                           lang="en",
                           since_id = date,
                           tweet_mode = 'extended').items(tweetNum)

    #we put data on a list to access them
    tweetsList = [tweet for tweet in tweets]
    csvList = list()
    i = 1
    for tweet in tweetsList:
        user = api.get_user(screen_name=tweet.user.screen_name)
        user_id = user.id
        username = tweet.user.screen_name
        location = tweet.user.location
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count
        retweetcount = tweet.retweet_count
        hashtags = tweet.entities['hashtags']

        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])

        info = [user_id,
                username,
                location,
                following,
                followers,
                totaltweets,
                retweetcount,
                text,
                hashtext]

        #to get all data
        data.loc[len(data)] = info
        csvList.append(toList(info))
    toCsv(csvList)

#This method will be used to add the data of each column as lists
#to the final list that will be used to save them to csv
def toList(data):
    #we check if there are not relative data to remove them
    if not data[8] or 'FIFAWorldCup' not in data[8]:
        return
    result = list()
    result.append(f"{data[0]}")
    result.append(f"{data[1]}")
    result.append(f"{data[2]}")
    result.append(f"{data[3]}")
    result.append(f"{data[4]}")
    result.append(f"{data[5]}")
    result.append(f"{data[6]}")
    result.append(f"{data[7]}")
    result.append(f"{data[8]}")
    return result

#method to save the data to csv
def toCsv(list):
    headers = ['user_id',
               'username',
               'location',
               'following',
               'followers',
               'totaltweets',
               'retweetcount',
               'text',
               'hashtags']
    #save to csv, new line is set to "" so as not to exist empty lines between the data
    with open('dataset.csv', 'w', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for item in list:
            if item != None:
                writer.writerow(item)

def createEdges():
    idList = list()
    headers = ['user_id', 'friend_id']
    with open("dataset.csv", 'r') as data, open("edges.csv", 'w', encoding='utf-8', newline='') as edges:
        reader =  csv.reader(data, delimiter=';')
        writer = csv.writer(edges)
        writer.writerow(headers)
        next(reader) #to skip the headers
        for row in reader:
            idList.append(int(row[0]))
        rows = list()
        count = 0
        for id in idList:
            count+=1
            print(count)
            friends = api.get_friend_ids(user_id=id)
            for friend in friends:
                if friend in idList:
                    newRow = [friend,id]
                    rows.append(newRow)
        writer.writerows(rows)

#method to add a field to the dataset.
#data will be a list with all the columns and their values that we want to add to the dataset
def addField(data):
    with open('dataset.csv', 'rw', newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        if not data:
            print("Invalid data, please use a valid input!")
            return
        for item in data:
            if not item:
                print("Invalid data. Your data contain invalid items!")
                return
            writer.writerow(item)


def main():
    authentication()
    #to make sure authentication will happen first, we wait for three seconds
    time.sleep(3.0)
    #initData("#FifaWorldCup","2022--12--18",500)

    createEdges()


if __name__ == "__main__":
    main()
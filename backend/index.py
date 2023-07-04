from flask import Flask
from time import sleep
from dotenv import load_dotenv
from os import getenv
import text2emotion as te
import requests
import json
import csv

load_dotenv()
app = Flask(__name__)


@app.route('/api/getNews', methods=['GET'])
def getNews():
    return getAllNews(countryCodesPath="countryCodes.csv", newsPath="news.json", apiKey=getenv('API_KEY'), language='en', numberOfArticles=40, startDate='2023-06-03 00:00:00', endDate='2023-07-03 12:40:00')


@app.route('/api/getSentiment/<countryCode>', methods = ['GET'])
def getSentiment(countryCode):
    return "Sentiment for " + countryCode


@app.route('/api/getEmotions', methods = ['GET'])
def getEmotions():
    return analyzeAllNews(news=getNews(), emotionsPath='emotions.json', newsPath='news.json')
    



def getCountryCodes(path):
    countryCodes = []
    # Open the csv file
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        
        # Read through the file except the first line
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                # Append each country code, but discard the extra quotes and spaces
                countryCodes.append(row[1].replace('\"', '').replace(' ', ''))
                line_count += 1

    return countryCodes


def getNewsByCountry(apiKey, countryCode, language, numberOfArticles, startDate, endDate):
    # Create the url for the news api request
    url = "https://api.worldnewsapi.com/search-news?"
    url += "api-key=" + apiKey
    url += "&source-countries=" + countryCode
    url += "&language=" + language
    url += "&number=" + str(numberOfArticles)
    url += "&earliest-publish-date=" + startDate
    url += "&latest-publish-date=" + endDate

    print(f"REQUEST URL: {url}")
    
    # Request the data from the news api
    result = requests.get(url)
    # If there is some error in the 
    if (result.status_code != 200):
        print("ERROR WITH REQUEST")
        return False
    
    # Create object to add to news array
    countryNews = {
        "countryCode": countryCode,
        "articles": result.json()['news']
    }

    return countryNews


def saveNews(path, news):
    # Open and dump the dictionary object into the chosen file
    with open(path, 'w') as json_file:
        json.dump(news, json_file)


def getAllNews(countryCodesPath, newsPath, apiKey, language, numberOfArticles, startDate, endDate, reset=False):
    print(f"APIKEY: {apiKey}")
    # Gets country codes in order to make requests
    print("ATTEMPTING TO GATHER COUNTRY CODES")
    countryCodes = getCountryCodes(countryCodesPath)
    print(countryCodes)

    # If the news data is not being reset, load it from the file
    news = []
    if not reset:
        print("ATTEMPTING TO LOAD PREVIOUS NEWS")
        with open(newsPath, 'r') as json_file:
            news = json.load(json_file) 

    print("ATTEMPTING TO UPDATE NEWS DATA")
    count = 0
    failCount = 0
    try:
        # Iterate through each country
        for countryCode in countryCodes:
            # if count > 2:
            #     break
            # If the country already has data stored, skip making another request
            skip = False
            for country in news:
                if country['countryCode'] == countryCode:
                    skip = True
                    break
            if skip:
                print(f"COUNTRY {countryCode} ALREADY PRESENT. SKIPPING")
                continue

            # Get the news for the country
            countryNews = getNewsByCountry(apiKey=apiKey, countryCode=countryCode, language=language, numberOfArticles=numberOfArticles, startDate=startDate, endDate=endDate)
            # Check if the request was valid and append if so
            if countryNews == False:
                failCount += 1
                if failCount > 5:
                    break
                print("INVALID REQUEST")
                continue
            else:
                failCount = 0
                news.append(countryNews)
            
                
            # Can only make 1 request/sec so this avoids limiters
            print(f"NEWS GRAB ITERATIONS: {count}")
            count += 1
            sleep(1.5)
    # If there is an error save the current news data
    except Exception as e:
        print(e)
        saveNews(newsPath, news=news)
        return news
    
    # Save all the news data
    saveNews(newsPath, news=news)
    return news


def analyzeAllNews(news, emotionsPath, newsPath):
    emotionsByCountry = []
    for country in news:
        print(f"STARTING ANALYSIS ON: {country['countryCode']}")
        totalEmotions = {
            'Angry': 0,
            'Fear': 0,
            'Happy': 0,
            'Sad': 0,
            'Surprise': 0
        }
        articleCount = 0
        for article in country['articles']:
            print(f"ANALYZING ARTICLE: {article['title']}")
            emotions = te.get_emotion(article['text'])
            article['emotions'] = emotions

            totalEmotions['Angry'] += emotions['Angry']
            totalEmotions['Fear'] += emotions['Fear']
            totalEmotions['Happy'] += emotions['Happy']
            totalEmotions['Sad'] += emotions['Sad']
            totalEmotions['Surprise'] += emotions['Surprise']
            articleCount += 1
        
        if articleCount == 0:
            emotionsByCountry.append({
                "countryCode": country["countryCode"],
                "emotions": totalEmotions
            })
            continue

        
        totalEmotions['Angry'] = totalEmotions['Angry'] / articleCount
        totalEmotions['Fear'] = totalEmotions['Fear'] / articleCount
        totalEmotions['Happy'] = totalEmotions['Happy'] /articleCount
        totalEmotions['Sad'] = totalEmotions['Sad'] / articleCount
        totalEmotions['Surprise'] = totalEmotions['Surprise'] / articleCount
        print(f"ANALYZED EMOTIONS: {totalEmotions}")
        emotionsByCountry.append({
            "countryCode": country["countryCode"],
            "emotions": totalEmotions
        })
        saveNews(news=news, path=newsPath)
        saveAnalysis(emotions=emotionsByCountry, emotionsPath=emotionsPath)

    saveAnalysis(emotions=emotionsByCountry, emotionsPath=emotionsPath)
    return emotionsByCountry


def saveAnalysis(emotions, emotionsPath):
    with open(emotionsPath, 'w') as json_file:
        json.dump(emotions, json_file)


if __name__ == '__main__':
   app.run()
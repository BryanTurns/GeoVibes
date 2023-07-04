from flask import Flask
from time import sleep
from dotenv import load_dotenv
from os import getenv
import text2emotion as te
from flask_apscheduler import APScheduler
import requests
import json
import csv

load_dotenv()
app = Flask(__name__)


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


def getNews(apiKey, numberOfArticles, startDate, endDate, reset=False, newsPath='news.json', countryCodesPath='countryCodes.csv', language='en'):
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



def getNewsUsingCountryCodes(apiKey, numberOfArticles, startDate, endDate, countryCodes, newsPath='news.json', language='en'):
    print("ATTEMPTING TO LOAD PREVIOUS NEWS")
    with open(newsPath, 'r') as json_file:
        news = json.load(json_file) 

    count = 0
    failCount = 0
    # Get the news for the country
    # NEED TO DELETE OLD NEWS AND ADD NEW NEWS
    try:
        for countryCode in countryCodes:
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

    except Exception as e:
        print(e)
        saveNews(path=newsPath, news=news)
        return news

def getSplitCountryCodes(countryCodes, maxSize=50):
    splitCodes = []
    count = 0
    tempArray = []
    for code in countryCodes:
        tempArray.append(code)

        if count > maxSize:
            splitCodes.append(tempArray)
            tempArray = []
        
        count += 1
    
    return splitCodes

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

splitCountryCodes =  getSplitCountryCodes(getCountryCodes('countryCodes.csv'))
currentSplit = 0

def updateCountryNews():
    global splitCountryCodes
    global currentSplit
    getNewsUsingCountryCodes(apiKey=getenv('API_KEY'), numberOfArticles=40, startDate='2023-06-03 00:00:00', endDate='2023-07-03 12:40:00', countryCodes=splitCountryCodes[currentSplit])
    currentSplit += 1
    if currentSplit > len(splitCountryCodes)-1:
        currentSplit = 0


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(id='test-job', func=updateCountryNews, trigger='interval', hours=24)


@app.route('/api/getAllNews', methods=['GET'])
def getAllNews():
    return getNews(getenv('API_KEY'), 40, '2023-06-03 00:00:00', '2023-07-03 12:40:00')


@app.route('/api/getAllSentiment/<countryCode>', methods = ['GET'])
def getSentiment(countryCode):
    return "Sentiment for " + countryCode


@app.route('/api/getEmotions', methods = ['GET'])
def getEmotions():
    return analyzeAllNews(news=getNews(), emotionsPath='emotions.json', newsPath='news.json')
    
@app.route('/api/getCountryNews/<countryCode>')
def getCountryNews(countryCode):
    news = []
    with open('news.json', 'r') as json_file:
        news = json.load(json_file)
    
    for country in news:
        if country['countryCode'] == countryCode:
            return country



    


def analyzeAllNews(news, emotionsPath, newsPath):
    emotionsByCountry = []
    # Iterate through the countries
    for country in news:
        print(f"STARTING ANALYSIS ON: {country['countryCode']}")
        # Initialize emotions dict and article counter 
        totalEmotions = {
            'Angry': 0,
            'Fear': 0,
            'Happy': 0,
            'Sad': 0,
            'Surprise': 0
        }
        articleCount = 0

        # Iterate over each article in the country
        for article in country['articles']:
            # If the article has already been analyzed, skip it
            if 'emotions' in article.keys(): 
                print(f"ARTICLE {article['title']} ALREADY ANALYZED")
                continue
            # Analyze the article
            print(f"ANALYZING ARTICLE: {article['title']}")
            emotions = te.get_emotion(article['text'])
            # Attach the analyzed emotions to the article to prevent rerunning
            article['emotions'] = emotions

            # Add emotions to emotion total for average per country
            totalEmotions['Angry'] += emotions['Angry']
            totalEmotions['Fear'] += emotions['Fear']
            totalEmotions['Happy'] += emotions['Happy']
            totalEmotions['Sad'] += emotions['Sad']
            totalEmotions['Surprise'] += emotions['Surprise']
            articleCount += 1
        
        # If there were no articles, set emotions to 0
        if articleCount == 0:
            emotionsByCountry.append({
                "countryCode": country["countryCode"],
                "emotions": totalEmotions
            })
            continue

        # Find average of each emotion
        totalEmotions['Angry'] = totalEmotions['Angry'] / articleCount
        totalEmotions['Fear'] = totalEmotions['Fear'] / articleCount
        totalEmotions['Happy'] = totalEmotions['Happy'] /articleCount
        totalEmotions['Sad'] = totalEmotions['Sad'] / articleCount
        totalEmotions['Surprise'] = totalEmotions['Surprise'] / articleCount
        print(f"ANALYZED EMOTIONS: {totalEmotions}")

        # Add the country and it's emotions to array
        emotionsByCountry.append({
            "countryCode": country["countryCode"],
            "emotions": totalEmotions
        })

        # Save the new news and analysis data for each country
        saveNews(news=news, path=newsPath)
        saveAnalysis(emotions=emotionsByCountry, emotionsPath=emotionsPath)

    # Save the news and analysis again incase update isn't caught
    saveNews(news=news, path=newsPath)
    saveAnalysis(emotions=emotionsByCountry, emotionsPath=emotionsPath)

    # Return the list of emotions by country
    return emotionsByCountry


def saveAnalysis(emotions, emotionsPath):
    with open(emotionsPath, 'w') as json_file:
        json.dump(emotions, json_file)


if __name__ == '__main__':
   app.run()
import json
import csv
from time import sleep
import text2emotion as te
import requests


def fetchNewsFromAllCountries(apiKey, numberOfArticles, startDate, endDate, reset=False, newsPath='news.json', countryCodesPath='countryCodes.csv', language='en'):
    # Gets country codes in order to make requests
    countryCodes = getCountryCodes(countryCodesPath)

    # If the news data is not being reset, load it from the file
    news = []
    if not reset:
        with open(newsPath, 'r') as json_file:
            news = json.load(json_file) 

    count = 0
    failCount = 0
    try:
        # Iterate through each country
        for countryCode in countryCodes:
            # If the country already has data stored, skip making another request
            skip = False
            for country in news:
                if country['countryCode'] == countryCode:
                    skip = True
                    break
            if skip:
                continue

            # Get the news for the country
            countryNews = getNewsByCountries(apiKey=apiKey, countryCode=countryCode, language=language, numberOfArticles=numberOfArticles, startDate=startDate, endDate=endDate)
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
            count += 1
            sleep(1.5)
    # If there is an error save the current news data
    except Exception as e:
        print(e)
        with open(newsPath, 'r') as json_file:
            json.dump(news, json_file)

        return news
    
    # Save all the news data
    with open(newsPath, 'r') as json_file:
            json.dump(news, json_file)
    return news


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


def saveNews(path, news):
    # Open and dump the dictionary object into the chosen file
    with open(path, 'w') as json_file:
        json.dump(news, json_file)


def saveAnalysis(emotions, emotionsPath):
    with open(emotionsPath, 'w') as json_file:
        json.dump(emotions, json_file)


def getNewsByCountries(apiKey, countryCode, language, numberOfArticles, startDate, endDate):
    # Create the url for the news api request
    url = "https://api.worldnewsapi.com/search-news?"
    url += "api-key=" + apiKey
    url += "&source-countries=" + countryCode
    url += "&language=" + language
    url += "&number=" + str(numberOfArticles)
    url += "&earliest-publish-date=" + startDate
    url += "&latest-publish-date=" + endDate
    
    # Request the data from the news api
    result = requests.get(url)
    # If there is some error in the 
    if (result.status_code != 200):
        return False
    
    # Create object to add to news array
    countryNews = {
        "countryCode": countryCode,
        "articles": result.json()['news']
    }

    return countryNews


def fetchNewsByCountryCodes(apiKey, numberOfArticles, startDate, endDate, countryCodes, newsPath='news.json', language='en'):
    print("ATTEMPTING TO LOAD PREVIOUS NEWS")
    with open(newsPath, 'r') as json_file:
        news = json.load(json_file) 

    count = 0
    failCount = 0
    # Get the news for the country
    # NEED TO DELETE OLD NEWS AND ADD NEW NEWS
    try:
        for countryCode in countryCodes:
            countryNews = getNewsByCountries(apiKey=apiKey, countryCode=countryCode, language=language, numberOfArticles=numberOfArticles, startDate=startDate, endDate=endDate)
            # Check if the request was valid and append if so
            if countryNews == False:
                failCount += 1
                if failCount > 5:
                    break
                continue
            else:
                failCount = 0
                news.append(countryNews)

            # Can only make 1 request/sec so this avoids limiters
            count += 1
            sleep(1.5)

    except Exception as e:
        print(e)
        with open(newsPath, 'w') as json_file:
            json.dump(news, json_file)

        return news


def splitArray(array, maxSize=50):
    newArray = []
    count = 0
    tempArray = []
    for item in array:
        tempArray.append(item)

        if count > maxSize:
            newArray.append(tempArray)
            tempArray = []
        
        count += 1
    
    return newArray


def analyzeAllNews(news, emotionsPath, newsPath):
    emotionsByCountry = []
    # Iterate through the countries
    for country in news:
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
                articleCount += 1
                totalEmotions['Angry'] += article['emotions']['Angry']
                totalEmotions['Fear'] += article['emotions']['Fear']
                totalEmotions['Happy'] += article['emotions']['Happy']
                totalEmotions['Sad'] += article['emotions']['Sad']
                totalEmotions['Surprise'] += article['emotions']['Surprise']
                continue
            # Analyze the article
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

        # Add the country and it's emotions to array
        emotionsByCountry.append({
            "countryCode": country["countryCode"],
            "emotions": totalEmotions
        })

        # Save the new news and analysis data for each country
        with open(newsPath, 'w')  as json_file:
            json.dump(news, json_file)
        with open(emotionsPath, 'w') as json_file:
            json.dump(emotionsByCountry, json_file)

    # Save the news and analysis again incase update isn't caught
    with open(newsPath, 'w')  as json_file:
        json.dump(news, json_file)
    with open(emotionsPath, 'w') as json_file:
        json.dump(emotionsByCountry, json_file)
    # Return the list of emotions by country
    return emotionsByCountry



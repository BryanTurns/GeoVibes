from flask import Flask
from dotenv import load_dotenv
from os import getenv
from flask_apscheduler import APScheduler
import json
from flask_cors import CORS, cross_origin
from utility import getCountryCodes, getNewsUsingCountryCodes, splitArray
import datetime


load_dotenv()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


splitCountryCodes =  splitArray(getCountryCodes('countryCodes.csv'))
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
@cross_origin()
def getAllNews():
    with open('news.json', 'r') as json_file:
        return json.load(json_file)


@app.route('/api/getEmotions', methods = ['GET'])
@cross_origin()
def getEmotions():
    emotions = []
    with open('emotions.json') as json_file:
        emotions = json.load(json_file)
    
    return emotions
    

@app.route('/api/getCountryNews/<countryCode>')
@cross_origin()
def getCountryNews(countryCode):
    news = []
    with open('news.json', 'r') as json_file:
        news = json.load(json_file)
    
    for country in news:
        if country['countryCode'] == countryCode.upper():
            return country
        
    return { "country": countryCode.upper(), 'articles': []}


@app.route('/api/getCountryEmotions/<countryCode>')
@cross_origin()
def getCountryEmotions(countryCode):
    emotions = []
    with open('emotions.json', 'r') as json_file:
        emotions = json.load(json_file)

    for country in emotions:
        if country['countryCode'] == countryCode.upper():
            return country
        
    return { "country": countryCode.upper(), 'emotions': []}
    

if __name__ == '__main__':
   app.run()
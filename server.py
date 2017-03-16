#!/usr/bin/python

from flask import Flask, request, redirect, render_template
from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
import twilio.twiml
import random
import requests
import json
import omdb
from googleplaces import GooglePlaces, types, lang
from microsofttranslator import Translator
from yahoo_finance import Share

gp_api_key = 'AIzaSyAX_75N29J--rh3Qj9gXjMBVx9IuD_Um74'
google_places = GooglePlaces(gp_api_key)

bing_api_key = 'oeToVPEyRZIASRK2n2byOU1x0EMatLIpd8kCIvwXmMw'

# Credentials owner: avikantsainidbz@gmail.com
# Find these values at https://twilio.com/user/account
twilio_account_sid = "ACab3e465e67051257d227bf49a3c9a58e"
twilio_auth_token = "ca96731e12b0442bcf5b1c8f7dedc58d"

admin_phone = "+918095138333"
# admin_phone = "+918095718111"

test_mode = False

# For TESTing -- START
from twilio.rest import TwilioRestClient
# For TESTing -- END

app = Flask(__name__)
app.config.from_object('config')

# Main route

class SMSForm(Form):
    phone_number = StringField('phone_number', validators=[DataRequired()])
    query_string = StringField('query_string', validators=[DataRequired()])

@app.route("/", methods=['GET', 'POST'])
def home_page():
    form = SMSForm()
    if form.validate_on_submit():
        query = str(form.query_string.data)
        number = str(form.phone_number.data)
        print("Sending sms to " + number + " with query \'" + query + "\'.")
        message = process_query(query)
        send_sms_to_number(message, number)
        return redirect('/')
    return render_template('index.html', form=form)


# Test routes

def send_sms_to_number(message, number):
    client = TwilioRestClient(twilio_account_sid, twilio_auth_token)
    message = client.messages.create(to=number, from_="+13609001701", body=message)

def send_sms_to_admin(message):
    send_sms_to_number(message, admin_phone)

# Test routing to specific phone number
@app.route("/test_phone/<phone>", methods=['POST'])
def test_method(phone):
    try:
        query = request.form.get('query')
        msg = process_query(query)
        send_sms_to_number(str(msg), phone)
        return "Message \'\'\'" + str(msg) + "\'\'\' sent to " + str(phone) + ".\n"
    except:
        return "Failed to send message. :(\n"
    
# Main routes

noIntent = [
    "I'm having trouble understanding you, could you rephrase your question?",
    "I didn't catch that, could you rephrase your query?",
    "Sorry, I didn't understand that. Try rephrasing your request."
]

technicalIssues = [
    "Looks like we are facing technical difficulties, please try again in sometime.",
    "Looks like the server is taking to long to respond, please try again in sometime.",
    "Looks like we have too many requests to handle at the moment, please try again in sometime."
    "Our monkeys are fixing some bugs in the server, please try again in sometime."
]

@app.route("/no_intent", methods=['POST'])
def no_intent():
    message = random.choice(noIntent)
    return message

@app.route("/network_error", methods=['POST'])
def technical_issues():
    message = random.choice(technicalIssues)
    return message

@app.route("/sos", methods=["POST"])
def sos(dict_response):
    message = ""
    try:
        query_text = dict_response["_text"].lower()

        # remove sos prefix and clean location string
        if query_text.find("sos ") != -1:
            query_text = query_text[4:]
        if query_text.find(" sos") != -1:
            query_text = query_text[:-4]
        if query_text.find("help ") != -1:
            query_text = query_text[5:]
        if query_text.find(" help") != -1:
            query_text = query_text[:-5]

        query_result = google_places.nearby_search(location=query_text, keyword='hospital', radius=5000, types=[types.TYPE_HOSPITAL])

        number_of_places = 0
        message = "List of Hospitals:\n"

        for place in query_result.places:
            if number_of_places < 3:
                number_of_places += 1
                message = message + place.name
                place_info = place.get_details()
                message = message + ", Ph: " + place.local_phone_number + "\n"
            else:
                break
    except:
        message = technical_issues()

    return message

@app.route("/weather", methods=['POST'])
def weather(entities):
    location = entities['location'][0]['value'].lower()
    message = ""
    response = requests.get(url="http://api.openweathermap.org/data/2.5/weather?q=" + location + "&APPID=500d01a6ece6498b1cbf94ed23519119")

    try:
        dict_response = json.loads(response.text)

        temperature_in_celsius = round(dict_response['main']['temp'] - 273.15, 2)
        humidity = dict_response['main']['humidity']
        weather_description = dict_response['weather'][0]['description']

        message = "The weather in " + location + ": " + weather_description + ". "
        message += "Average: " + str(temperature_in_celsius) + " C, "
        message += "Humidity: " + str(humidity) + "%"

        try:
            wind_speed = dict_response['wind']['speed']
            message += ", Wind: " + str(wind_speed) + " km/h"
        except:
            message += "."
    except:
        message = technical_issues()

    return message

@app.route("/navigate", methods=['POST'])
def navigate(entities):
    destination = entities['to'][0]['value']
    origin = entities['from'][0]['value'].lower()
    message = ""

    key = "GSC5hkB0CEmUyk4nI2MY~HxNEzo1P1bHB1sX8EzDJpA~AmYeCHqvBerEI06DBSKWfo4pgB1w9Krgk7EH6lhGqqf3s5RaJArOzWJ-SL6AYVVw"
    bingMapsResponse = requests.get(url="http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=" + origin + "&wp.1=" + destination + "&avoid=minimizeTolls&key="+key)

    try:
        bingMaps_dict = json.loads(bingMapsResponse.text)
        resources = bingMaps_dict.get('resourceSets')[0].get('resources')
        routeLegs = resources[0].get('routeLegs')
        message = ""
        distance = routeLegs[0].get('routeSubLegs')[0].get('travelDistance')
        message += "Total Trip Distance: " + str(distance) + " km\n"
        duration = routeLegs[0].get('routeSubLegs')[0].get('travelDuration')
        message += "Total Trip Duration: " + str(duration/60) + " min \n"
        itineraryItems = routeLegs[0].get('itineraryItems')
        count = 1
        for item in itineraryItems:
            message += str(count) + ". " + item.get('instruction').get('text') + " ("
            message += str(item.get('travelDistance')) + " km, "
            message += str(item.get('travelDuration') / 60 ) + " min)"
            message += "\n"
            count +=1

        # Precaution
        if (len(message) > 1536):
            message = message[:1533] + "...";

    except:
        message = technical_issues()

    return message

@app.route("/translate", methods=['POST'])
def translate(entities):
    message = ""

    try:
        text_for_translation = entities['phrase_to_translate'][0]['value']
        language =  entities['language'][0]['value'].lower()
        if language == "spanish":
            language = "es"
        elif language == "french":
            language = "fr"
        elif language == "german":
            language = "de"
        elif language == "chinese":
            language = "zh-CHS"
        else:
            message = "Language not supported!"

        if message != "Language not supported!":
            message = "Translation for " + text_for_translation + " to " + language + ":\n"
            try:
                translator = Translator('SMSAssistant', 'fhV+AdYFiK0QfQ4PFys+oQ/T0xiBBVQa32kxxbP55Ks=')
            except:
                message = "Looks like we are facing technical difficulties. Please try again later."
                return message
            message += translator.translate(text_for_translation, language)
    except:
        message = technical_issues()

    return message

@app.route("/news", methods=['POST'])
def getNews(entities):
    message = ""
    try:
        try:
            newstopic = entities['news_topic'][0]['value'].lower()
            # default topic
            if newstopic is None:
                newstopic = "world"
        except:
            newstopic = "world"

        response = requests.get(url='https://api.datamarket.azure.com/Bing/Search/News?$format=json&Query=%27' + newstopic + "%27", \
         auth=(bing_api_key, bing_api_key))

        news_dict = json.loads(response.text)
        news = news_dict.get('d').get('results')

        message = ""
        if len(news) >= 5:
            message = "Here are the top 5 stories about " + newstopic + ":\n"
            for x in range(0, 5):
                message += str(x+1) + ". " + news[x].get('Title') + ".\n"
        else:
            message = "Here are the top news stories about " + newstopic + ":\n"
            for item in news:
                message += "- " + item.get('Title') + "\n"
        
        if test_mode:
            send_sms_to_admin(message)
    except:
        message = technical_issues()

    return message

@app.route("/imdb", methods=['POST'])
def imdb(dict_response):
    message = ""
    try:
        query_text = dict_response['_text'].lower()
        if query_text.find("imdb ") != -1:
            query_text = query_text[5:]

        response = omdb.request(t='' + query_text + '', r='json')
        data = json.loads(response.text)

        mediatype = data["Type"]
        year = data["Year"]
        title = data["Title"]
        if mediatype == "movie":
            message += "Found a Movie, \"" + title + "\" (" + year + ")\n"
        elif mediatype == "series":
            message += "Found a TV show, \"" + title + "\" (" + year + ")\n"
        for key in data:
            if key in ["Rated", "Runtime", "Genre", "Director", "Writer"]:
                if data[key] != "N/A":
                    message += key + ": " + data[key] + "\n"
            if key == "imdbRating":
                message += "IMDB: " + data[key] + "\n"
        if data["Plot"] != "N/A":
            message += "Plot: " + data["Plot"]
    except:
        message = technical_issues()
    return message

@app.route("/stocks", methods=['POST'])
def stocks(dict_response):
    message = ""
    try:
        query_text = dict_response['_text'].lower()
        if query_text.find("stocks ") != -1:
            query_text = query_text[7:]
        y = Share(query_text)
        message += "Trading information for " + y.get_name() + " (" + query_text + ") :\n"
        message += "Opened: " + y.get_open() + "\n"
        message += "Current: " + y.get_price() + "\n"
        message += "Earnings share: " + y.get_earnings_share() + "\n"
        message += "Short ratio: " + y.get_short_ratio() + "\n"
        message += "Previous close: " + y.get_prev_close() + "\n"
    except:
        message = technical_issues()
    return message

@app.route("/atm", methods=['POST'])
def atm(dict_response):
    message = ""
    try:
        query_text = dict_response['_text'].lower()
        if query_text.find("atm near ") != -1:
            query_text = query_text[9:]
        query_result = google_places.nearby_search(location=query_text, keyword='atm', radius=5000, types=[types.TYPE_ATM])

        number_of_places = 0
        message = ""

        for place in query_result.places:
            if number_of_places < 5:
                number_of_places += 1
                message = message + place.name
                place_info = place.get_details()
                if place.local_phone_number != None:
                    message = message + " " + place.local_phone_number
                message = message + "\n"
            else:
                break
    except:
        message = technical_issues()
    return message

@app.route("/define", methods=['POST'])
def define(dict_response):
    message = ""
    try:
        query_text = dict_response['_text'].lower()
        if query_text.find("define ") != -1:
            topic = query_text[7:]
        r = requests.get(url='http://api.duckduckgo.com/?q=' + topic + '&format=json&pretty=1')

        message = ""

        topic_response = json.loads(r.text)
        all_definitions = topic_response['RelatedTopics']
        if len(all_definitions) > 0:
            top_definitions = all_definitions[0]
            definition = top_definitions['Text']
            message = "\"" + topic + "\": " + definition
        else:
            message = "Definition not found"
    except:
        message = technical_issues()
    return message

# Main SMS webhook

def process_query(query):
    msg = ""
    try:
        response = requests.get(url='https://api.wit.ai/message?v=20161022&q='+query,headers={'Authorization': 'Bearer TUDKLORVVMITDT4FCJFMAARQAWB2NLJ2'})
    except:
        msg = technical_issues()
        return msg
    dict_response = json.loads(response.text)

    intent = None
    confidence = None
    entities = None
    msg = None

    try:
        if dict_response['entities']['intent']:
            intent = dict_response['entities']['intent'][0]['value']
            confidence = dict_response['entities']['intent'][0]['confidence']
            entities = dict_response['entities']
    except:
        msg = no_intent()
        return msg

    if intent is None or confidence < 0.2:
        msg = no_intent()
    elif intent == "weather":
        msg = weather(entities)
    elif intent == "navigate":
        msg = navigate(entities)
    elif intent == "sos":
        msg = sos(dict_response)
    elif intent == "translate":
        msg = translate(entities)
    elif intent == "news":
        msg = getNews(entities)
    elif intent == "imdb":
        msg = imdb(dict_response)
    elif intent == "atm":
        msg = atm(dict_response)
    elif intent == "stocks":
        msg = stocks(dict_response)
    elif intent == "define":
        msg = define(dict_response)
    else:
        msg = "Feature not supported"

    return msg

@app.route("/sms", methods=['POST'])
def sms():
    message_body = request.values.get('Body', None)
    resp = twilio.twiml.Response()
    msg = process_query(message_body)
    if test_mode:
        send_sms_to_admin(msg)
    resp.message(msg)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)

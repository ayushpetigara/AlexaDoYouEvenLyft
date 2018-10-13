import requests
from geopy.geocoders import GoogleV3
import random


try:
	TOKEN_VAL = open("token_val.txt").read().strip()
except:
	TOKEN_VAL = raw_input("Token Val: ")

try:
	GOOGLE_KEY = open("google_key.txt").read().strip()
except:
	GOOGLE_KEY = raw_input("Google API Key: ")

geolocator = GoogleV3(api_key=GOOGLE_KEY)
# Allows you to convert device location to Long/Lat

OPTIONS = ["A little more than", "approximately", "a little less than"]

headers = {
    'Authorization': 'Token {}'.format(TOKEN_VAL),
    'Accept-Language': 'en_US',
    'Content-Type': 'application/json',
}

def convertLatLong(address):
	a = geolocator.geocode(address)
	return {"Latitude": a.latitude, "Longitude": a.longitude}

def extractLatLong(event, context):
	try:
		deviceID = event["context"]["System"]['device']['deviceId']
	except:
		deviceID = "Test"
	try:
		key = event["context"]["System"]['apiAccessToken']
	except:
		key = ""
		deviceID = "Test"
	# This returns a dictionary object
	headers = {'Host': 'api.amazonalexa.com', 'Accept': 'application/json', 'Authorization': "Bearer {}".format(key)}
	url = 'https://api.amazonalexa.com/v1/devices/{}/settings/address'.format(deviceID)
	res = requests.get(url, headers=headers).json()
	return convertLatLong(res["addressLine1"] + " " + res["city"] + " " + res['stateOrRegion'])

def getAddress(event, context):
	try:
		deviceID = event["context"]["System"]['device']['deviceId']
	except:
		deviceID = "Test"
	try:
		key = event["context"]["System"]['apiAccessToken']
	except:
		key = ""
		deviceID = "Test"
	# This returns a dictionary object
	headers = {'Host': 'api.amazonalexa.com', 'Accept': 'application/json', 'Authorization': "Bearer {}".format(key)}
	url = 'https://api.amazonalexa.com/v1/devices/{}/settings/address'.format(deviceID)
	res = requests.get(url, headers=headers).json()
	return res["addressLine1"] + " " + res["city"] + " " + res['stateOrRegion']


def extract_info(longitude, latitude):
	information = []
	jsonVal = getUberInfo(longitude, latitude)
	for val in jsonVal['times']:
		arrival_time = val['estimate'] / 60
		vehicle_type = val['localized_display_name']
		information.append({"type": vehicle_type, "time": arrival_time})
	return information

def getUberInfo(longitude, latitude):
	params = (
    ('start_latitude', latitude),
    ('start_longitude', longitude),
	)
	response = requests.get('https://api.uber.com/v1.2/estimates/time', headers=headers, params=params)
	return response.json()

def returnSpeech(speech, endSession=True, text="", title=""):
	return {
		"version": "1.0",
		"sessionAttributes": {},
		"response": {
		"outputSpeech": {
		"type": "PlainText",
		"text": speech
			},
			"directives": [{
                "type": "Display.RenderTemplate",
                "template": {
                    "type": "BodyTemplate1",
                    "token": "T123",
                    "backButton": "HIDDEN",
                    "backgroundImage": {
                        "contentDescription": "Uber Logo",
                        "sources": [{
                            "url": "https://s3.amazonaws.com/christopherlambert/uber-logo.png"
                        }]
                    },
                    "title": title,
                    "textContent": {
                        "primaryText": {
                            "text": text,
                            "type": "PlainText"
                        }
                    }
                }
            }],
			"shouldEndSession": endSession
		  }
		}

def nearest_uber(longitude, latitude):
	all_info = extract_info(longitude, latitude)
	all_responses = []
	message = ".  If you would like to book a ride please download the oober app on your smartphone."
	if len(all_info) == 0:
		return "There are no Uber drivers in your area."
	time_val = all_info[0]['time']
	car_type = all_info[0]['type'].lower().replace("uber", "oober ")
	return "There is an {} driver {} {} Minutes from your location".format(car_type, random.choice(OPTIONS), time_val) + message



def on_intent(intent_request, session, event, context):
	# This means the person asked the skill to do an action
	intent_name = intent_request["intent"]["name"]
	# This is the name of the intent (Defined in the Alexa Skill Kit)
	if intent_name == 'nearestUber':
		# nearestUber intent
		location = extractLatLong(event, context)
		# Current location
		return nearest_uber(location['Longitude'], location['Latitude'])
		# Return the response for what day

def lambda_handler(event, context):
	if event["request"]["type"] == "LaunchRequest":
		response = ""
		all_info = extract_info(location['Longitude'], location['Latitude'])
		all_responses = []
		for i, results in enumerate(all_info):
			time_val = results['time']
			car_type = results['type'].lower().replace("uber", "oober ")
			all_responses.append("There is an {} driver {} {} Minutes from your location".format(car_type, random.choice(OPTIONS), time_val))
		message = ".  If you would like to book a ride please download the oober app on your smartphone."
		return returnSpeech('. and '.join(all_responses) + message)

if __name__ == '__main__':
	long_lats = [v.split(',') for v in open("test_long_lats.txt").read().split("\n") if len(v) > 0]
	for lng, lat in long_lats:
		print nearest_uber(lng, lat)

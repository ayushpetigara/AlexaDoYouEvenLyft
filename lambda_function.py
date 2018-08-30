import requests
from geopy.geocoders import GoogleV3



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

def lambda_handler(event, context):
	if event["request"]["type"] == "LaunchRequest":
		return on_launch(event["request"], event["session"])

	elif event["request"]["type"] == "IntentRequest":
		locationInfo = alexaHelper.extractLatLong(event, context)
		return on_intent(event["request"], event["session"], locationInfo=locationInfo)
	else:
		handle_session_end_request()



if __name__ == '__main__':
	long_lats = [v.split(',') for v in open("test_long_lats.txt").read().split("\n") if len(v) > 0]
	for lng, lat in long_lats:
		for val in extract_info(lng, lat):
			print("{} Will be here in {} Minutes".format(val['type'], val['time']))



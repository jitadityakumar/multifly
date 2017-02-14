# request using input params and then parse and display data
import json
import requests
from pprint import pprint
import io

url = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
api_key = 'AIzaSyBeZPDePamxPgJlV1ivqYdgBspO294lOGI'

# Read json request from file
with open('request/request.json') as request_file:
	request = json.load(request_file)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
req_json = json.dumps(request)
print("request = "+req_json)

# Make request to google flights api
#r = requests.post(url+'?key='+api_key, data=req_json, headers=headers)
#print("Status "+str(r.status_code))
#response = json.loads(r.text)

# read response from file
with open('response/response.json') as response_file:
    response = json.load(response_file)

# Print parsed response to console
print("Parse and print")
counter = 0
for tripOption in response["trips"]["tripOption"]:
	saleTotal = tripOption["saleTotal"]

	counter = counter + 1
	print("==========Trip number "+str(counter)+" - Cost: "+saleTotal+"==========")

	legCounter = 0
	for slice in tripOption["slice"]:
		duration= slice["duration"]
		hours = duration / 60
		mins  = duration % 60
		legCounter+=1
		print("Leg "+str(legCounter)+" - Total Duration : "+str(hours)+"h"+str(mins)+"m")

		for segment in slice["segment"]:
			carrier = segment["flight"]["carrier"]
			number  = segment["flight"]["number"]
			flight = carrier+"-"+number
			bookingCode = segment["bookingCode"]

			for leg in segment["leg"]:
				aircraft = leg["aircraft"]
				origin = leg["origin"]
				destination = leg["destination"]
				duration = leg["duration"]
				hours = duration / 60
				mins = duration % 60
				mileage = leg["mileage"]
				arrivalTime = leg["arrivalTime"]
				departureTime = leg["departureTime"]

				print(origin+"-"+destination+" "+flight+" "+bookingCode+" "+str(hours)+"h"+str(mins)+"m aircraft:"+aircraft+" mileage:"+str(mileage)+" Dep:"+departureTime+" Arr:"+arrivalTime)

			if 'connectionDuration' not in segment:
				continue
			connectionDuration = segment["connectionDuration"]
			hours = connectionDuration / 60
			mins  = connectionDuration % 60
			print("Connection : "+str(hours)+"h"+str(mins)+"m")

print("====================")
# Parse request
d = json.loads(req_json)
plan = ""

for slice in d["request"]["slice"]:
        origin = slice["origin"]
        destination = slice["destination"]
        plan = plan + origin + "-" + destination + "-"
plan = plan + str(d["request"]["solutions"])


filename = "response/response-"+plan+".json"
print("filename = "+filename)
# Write response to json file
with io.open(filename, 'w', encoding='utf-8') as outfile:
    outfile.write(unicode(json.dumps(response, ensure_ascii=False, sort_keys=True, indent=2)))

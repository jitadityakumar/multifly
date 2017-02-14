# request using input params and then parse and display data
import json
import requests
from pprint import pprint

url = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
api_key = 'AIzaSyBeZPDePamxPgJlV1ivqYdgBspO294lOGI'

print("Read request from file")
# Read json request from file
with open('request/request.json') as data_file:
	data = json.load(data_file)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
data_json = json.dumps(data)
print("request = "+data_json)

r = requests.post(url+'?key='+api_key, data=data_json, headers=headers)
print("Status "+str(r.status_code))
response = json.loads(r.text)

data = response

print("Parse and print")
counter = 0
for tripOption in data["trips"]["tripOption"]:
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


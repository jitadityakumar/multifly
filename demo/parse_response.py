# Read the json response from response.json and show only the details required
import json
from pprint import pprint

# Read response from file
with open('response.json') as data_file:
	data = json.load(data_file)

#pprint(data)

# trips
#print(data["trips"]["data"]["airport"][0]["code"])
#print(data["trips"]["data"]["airport"][1]["code"])

# tripOption
saleTotal= data["trips"]["tripOption"][0]["saleTotal"]
duration= data["trips"]["tripOption"][0]["slice"][0]["duration"]
hours = duration / 60
mins = duration % 60

#print("Sale total = "+saleTotal)
#print("Duration = "+str(duration))
#print("hours = "+str(hours))
#print("mins = "+str(mins))

counter = 0
for tripOption in data["trips"]["tripOption"]:
	saleTotal = tripOption["saleTotal"]

	counter = counter + 1
	print("==========Trip number "+str(counter)+"==========")

	for slice in tripOption["slice"]:
		duration= slice["duration"]
		hours = duration / 60
		mins  = duration % 60
		print("Price: "+saleTotal+" Duration : "+str(hours)+"h"+str(mins)+"m")

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


import json
import requests

print("Start script")

# set defaults
adultCount=1
solutions=10

origin = raw_input("Origin ")
destination = raw_input("Destination ")
date = raw_input("Date ")


url = 'https://www.googleapis.com/qpxExpress/v1/trips/search'
api_key = 'AIzaSyBeZPDePamxPgJlV1ivqYdgBspO294lOGI'

data={'request': { 'slice': [{ 'origin': origin, 'destination': destination, 'date': date}], 'passengers': {'adultCount': adultCount},'solutions': solutions}}

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
data_json = json.dumps(data)

r = requests.post(url+'?key='+api_key, data=data_json, headers=headers)
print(r.status_code)
response = json.loads(r.text)

print("Response = "+ r.text)

print("End script")

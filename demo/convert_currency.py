# Convert to EUR

import requests
import json
import io


url = "http://api.fixer.io/latest"
r = requests.get(url)
ccy_json = json.loads(r.text)

with io.open('ccy.json','w', encoding='utf-8') as outfile:
	outfile.write(unicode(json.dumps(ccy_json, ensure_ascii=False, sort_keys=True, indent=2)))

# From api
a="USD"
amount=100
url = ('http://api.fixer.io/latest?symbols=%s') % (a)
print url

r = requests.get(url)
response=json.loads(r.text)
factor=response["rates"][a]

print("Rate: "+str(factor))

b=float(amount)/float(factor)
b=round(b,2)
print(str(amount)+a+" = "+str(b)+" EUR")

# from file
with open("ccy.json") as outfile:
	ccy_json = json.load(outfile)

factor=ccy_json["rates"][a]
print("Rate: "+str(factor))

b=float(amount)/float(factor)
b=round(b,2)
print(str(amount)+a+" = "+str(b)+" EUR")

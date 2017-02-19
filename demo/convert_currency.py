# Convert to EUR

import requests
import json

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

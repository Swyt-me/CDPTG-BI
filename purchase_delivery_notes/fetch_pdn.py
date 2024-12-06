import requests
import json

url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/PurchaseDeliveryNotes"

payload = {}
headers = {
  'Cookie': 'B1SESSION=ec9dce62-ab02-11ef-8000-fa163e6a32ef; ROUTEID=.node6;clxservice=40834453311.3450350304.1822273024; ROUTEID=.node10; clxservice=2424906801.1.3400902464.1214006272',
  'Content-Type': 'application/json',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive'
}

response = requests.request("GET", url, headers=headers, data=payload)

with open('UGA.json', 'w') as file:
    json.dump(response.json(), file, indent=4)

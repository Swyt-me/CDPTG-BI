import requests
import json
import os
from datetime import datetime
import time
from datetime import timedelta


def get_sap_token(warehouse):
    url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/Login/"
    payload = "{\r\n    \"CompanyDB\": \"" + warehouse + "\",\r\n    \"Password\": \"Super@321\",\r\n    \"UserName\": \"manager\"\r\n}\r\n"
    headers = {
        'Content-Type': 'text/plain'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get('SessionId')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def fetch_ledger_data(token,warehouse,ledger_date):
    base_url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/view.svc/GetItemCostInDetailB1SLQuery?$filter=( DocDate eq '"+ ledger_date + "')"
    #base_url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/Items?$filter=contains(U_JumiaSKU1, '"+ sku_code + "') "
    #https://c20988hs01p01.cloudiax.com:50000/b1s/v1/view.svc/GetItemCostInDetailB1SLQuery?$filter=( DocDate eq '2024-08-07')
    headers = {
        'Cookie': f'B1SESSION={token}; ROUTEID=.node6;clxservice=40834453311.3450350304.1822273024',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    url = base_url
    while url:
        try:
            print(url)
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            data = response.json()
            save_ledger_data(data,warehouse,ledger_date)
            url = data.get('odata.nextLink')
            if url:
                url = base_url.split("?")[0] + url.split("GetItemCostInDetailB1SLQuery")[1]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return

def save_ledger_data(data, warehouse,ledger_date):
    date_str = datetime.now().strftime("%Y%m%d")
    directory = f"sap_ledger/{ledger_date}/{warehouse}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{directory}/ledger_data_{timestamp}.json"
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    #print(f"Data saved to {filename}")

warehouses = ['MAR1']

#['CIV', 'EGY', 'SEN','MAR1','KEN1','NGA','UGA','TEST']  # Add your warehouse values here

for warehouse in warehouses:
    print("processing " + warehouse)
    token = get_sap_token(warehouse)
    if token:
        ledger_date = datetime.now() - timedelta(days=1)
        for i in range(1000):
            date_str = ledger_date.strftime("%Y-%m-%d")
            time.sleep(2)
            print(f"Processing date: {date_str}")
            for warehouse in warehouses:
                print("processing " + warehouse)
                token = get_sap_token(warehouse)
                if token:
                    fetch_ledger_data(token, warehouse, date_str)
                else:
                    print(f"Failed to retrieve SAP token for warehouse: {warehouse}")
            ledger_date -= timedelta(days=1)
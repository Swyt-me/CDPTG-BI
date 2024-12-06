import requests
import json
import os
from datetime import datetime
import csv

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

def fetch_items_data(token,warehouse,sku_code):
    base_url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/Items?$filter=contains(ItemCode, '"+ sku_code + "') "
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
            save_items_data(data,warehouse)
            url = data.get('odata.nextLink')
            if url:
                url = base_url.split("?")[0] + url.split("Items")[1]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return

def fetch_items_data_by_warehouse(token,warehouse):
    base_url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/Items?$filter=QuantityOnStock ge 1"
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
            save_items_data(data,warehouse)
            url = data.get('odata.nextLink')
            if url:
                url = base_url.split("?")[0] + url.split("Items")[1]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return


def save_items_data(data, warehouse):
    directory = f"item_json/{warehouse}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{directory}/items_data_{timestamp}.json"
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")

# Example usage

sku_codes = []

# Read item codes and warehouses from CSV
warehouses = set()
warehouse_sku_dict = {}

with open('itemcodes.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        item_code = row['itemcode']
        parsed_code = item_code.split('/')[1] if '/' in item_code else item_code
        warehouse = row['warehouse']
        
        if warehouse not in warehouse_sku_dict:
            warehouse_sku_dict[warehouse] = []
        
        warehouse_sku_dict[warehouse].append(parsed_code)
print(warehouse_sku_dict)
# Example usage
for warehouse, sku_codes in warehouse_sku_dict.items():
    token = get_sap_token(warehouse)
    if token:
        for item_code in sku_codes:
            fetch_items_data(token, warehouse, item_code)
            #print(item_code)
            #print(warehouse)
        # fetch_items_data_by_warehouse(token, warehouse)
    else:
        print(f"Failed to retrieve SAP token for warehouse: {warehouse}")
'''
warehouses = list(warehouses)

for warehouse in warehouses:
    token = get_sap_token(warehouse)
    if token:
        for item_code in sku_codes:
            fetch_items_data(token, warehouse, item_code)
        # fetch_items_data_by_warehouse(token, warehouse)
    else:
        print(f"Failed to retrieve SAP token for warehouse: {warehouse}")

'''
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
    
def fetch_additional_pdn_data(token,warehouse,creation_date):
    base_url = "https://c20988hs01p01.cloudiax.com:50000/b1s/v1/$crossjoin(PurchaseDeliveryNotes,PurchaseDeliveryNotes/DocumentLines)?$expand=PurchaseDeliveryNotes($select=DocEntry,DocNum,CreationDate,CardCode,CardName,DocCurrency,DocRate,NumAtCard,Reference1,Comments,JournalMemo),PurchaseDeliveryNotes/DocumentLines($select=ItemCode,ItemDescription,ShipDate,Quantity,Price,PriceAfterVAT,Currency,WarehouseCode,Rate,BarCode,GrossPrice,GrossTotal,U_RRP,U_Article,U_JumiaSKU,U_FOC,UnitsOfMeasurment)&$filter=PurchaseDeliveryNotes/DocEntry eq PurchaseDeliveryNotes/DocumentLines/DocEntry and PurchaseDeliveryNotes/CreationDate eq datetime' " + creation_date + "'"
    
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
            time.sleep(2)
            print(url)
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            data = response.json()
            save_pdn_additional_data(data,warehouse,creation_date)
            url = data.get('odata.nextLink')
            print("next link")
            print(url)
            print("base url")
            print(base_url)
            #break
            if url:
                url = base_url.split("?")[0] + url.split("crossjoin(PurchaseDeliveryNotes,PurchaseDeliveryNotes/DocumentLines)")[1]
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return
        
def save_pdn_additional_data(data, warehouse,creation_date):
    date_str = datetime.now().strftime("%Y%m%d")
    directory = f"sap_pdn_additional/{creation_date}/{warehouse}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{directory}/invoice_data_{timestamp}.json"
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    #print(f"Data saved to {filename}")

warehouses = ['KEN1']

for warehouse in warehouses:
    print("processing " + warehouse)
    token = get_sap_token(warehouse)
    if token:
        creation_date = datetime.strptime("2024-04-13", "%Y-%m-%d")
        for i in range(180):
            date_str = creation_date.strftime("%Y-%m-%d")
            time.sleep(1)
            print(f"Processing date: {date_str}")
            for warehouse in warehouses:
                print("processing " + warehouse)
                token = get_sap_token(warehouse)
                if token:
                    fetch_additional_pdn_data(token, warehouse, date_str)
                else:
                    print(f"Failed to retrieve SAP token for warehouse: {warehouse}")
            creation_date -= timedelta(days=1)
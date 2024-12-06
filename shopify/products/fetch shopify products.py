import datetime
import requests
import json
import pandas as pd
import configparser
import time


import os
from requests.auth import HTTPBasicAuth



API_KEY = 'a820d4688f5a1dbea49e12d271df3658'
PASSWORD = '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'
SHOP_NAME = 'mojaa-staging'
API_VERSION = '2024-01'

def get_yesterday_date():
    try:
        # Get today's date
        today = datetime.datetime.now()

        # Calculate yesterday by subtracting one day from today
        yesterday = today - datetime.timedelta(days=1)
        # Format the date as YYYY-MM-DD
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        # print(yesterday_str)
        return yesterday_str
    except Exception as e:
        print("Exception raised for def get_yesterday_date methord  - {}".format(str(e))) 

def get_today_date():
    try:
        # Get today's date
        today = datetime.now()

        # Calculate yesterday by subtracting one day from today
        yesterday = today - datetime.timedelta(days=1)
        # Format the date as YYYY-MM-DD
        today_str = today.strftime('%Y-%m-%d')
        # print(yesterday_str)
        return today_str
    except Exception as e:
        print("Exception raised for def get_today_date methord  - {}".format(str(e))) 

def get_shopify_url_response(api_type,params):
    try:
        # Shopify store API URL
        url = f"https://{API_KEY}:{PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/2024-01/{api_type}.json"
        # Send a GET request
        if params == '':
            response = requests.get(url)
        else:
            response = requests.get(url,params)    

        # Check if the request was successful
        if response.status_code == 200:
            resp = response.json()
            # print(json.dumps(products, indent=4))
        else:
            resp = None
            print(f"Error: {response.status_code}, {response.text}")
        return  resp   
    except Exception as e:
        print("Exception raised for def get_shopify_url_response methord  - {}".format(str(e)))   

def get_product_details(product_id):
    api_type = f"products"
    params = {
        "limit": 10  # Adjust the limit as per your requirement (max 250)
    }
    return get_shopify_url_response(api_type,params)

def get_shopify_orders_df():
    try:
        api_type = 'orders'
        dt = f''' {get_yesterday_date()}T00:00:00Z'''
        # created_at_min = '''2024-09-01T00:00:00Z'''  # Minimum creation date (ISO 8601 format)
        # created_at_max = '''2024-09-24T00:00:00Z'''  # Maximum creation date (ISO 8601 format)
        updated_at_min = dt
        status = "cancelled"
        params = {
                "updated_at_min": updated_at_min,
                # "created_at_max": created_at_max,
                 "status" : 'any',
                "limit": 250  # Adjust the limit as per your requirement (max 250)
        }
        # params = {"limit": 250}
        data = get_shopify_url_response(api_type, params)
        
        # Save the JSON object data as a JSON file
        with open('shopify_orders.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        # data = products
        df = pd.json_normalize(data['orders'])
        df['status']='success'
        return df
    except Exception as e:
        print("Exception raised for def get_shopify_orders_df methord  - {}".format(str(e)))   

def save_to_json(data, filename):
    """
    Saves data to a JSON file.
    
    Args:
        data (dict): The data to save.
        filename (str): The name of the JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

def fetch_all_products():
    products = []
    limit = 250  # Maximum allowed by Shopify
    since_id = None
    batch_number = 1  # To track batch numbers for file naming

    while True:
        params = {'limit': limit}
        if since_id:
            params['since_id'] = since_id

        response = requests.get(
            f"https://{API_KEY}:{PASSWORD}@{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json",
            params=params
        )

        if response.status_code == 429:
            # Rate limit exceeded; wait and retry
            print("Rate limit exceeded. Waiting before retrying...")
            time.sleep(2)  # Wait for 2 seconds before retrying
            continue
        elif response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        products.extend(data['products'])

        # Save the current batch to a JSON file
        save_to_json(data, f'products_batch_{batch_number}.json')
        batch_number += 1

        if len(data['products']) < limit:
            # Fetched all products
            break

        # Set since_id to the ID of the last product in the current batch
        since_id = data['products'][-1]['id']

        # Monitor API call limit
        api_call_limit = response.headers.get('X-Shopify-Shop-Api-Call-Limit', '0/40')
        current_calls, max_calls = map(int, api_call_limit.split('/'))
        if current_calls >= max_calls - 2:
            # Approaching rate limit; wait before next request
            time.sleep(0.5)  # Wait for 0.5 seconds

    return products

# Usage
all_products = fetch_all_products()
print(f"Total products fetched: {len(all_products)}")
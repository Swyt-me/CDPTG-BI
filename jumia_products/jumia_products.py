import requests
import os
import time
import json

def fetch_products(api_url, token, shop_id, size=10, next_token=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Cookie': '__cf_bm=iHSOWzl8ZfvcSKIeYSxRIlC0egrmY29vRcMseJUzGF0-1727969725-1.0.1.1-mL6QjOVXWhfkc_QiWv3ETwBQQZefAJI63zhhItrLo8TlVXMy8o4IczWQXh0_MQRix3rqrFi8arjCOIv1C_GWNg'
    }
    params = {
        'shopId': shop_id,
        'size': size
    }
    if next_token:
        params['token'] = next_token

    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def save_to_file(data, shop_id, page):
    folder_path = os.path.join('jumia_products', shop_id)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'products_page_{page}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def fetch_all_products(api_url, token, shop_id):
    next_token = None
    page = 1
    while True:
        try:
            products = fetch_products(api_url, token, shop_id, next_token=next_token)
            save_to_file(products, shop_id, page)
            print(f"Page {page} fetched and saved.")
            next_token = products.get('nextToken')
            is_last_page = products.get('isLastPage', False)
            if is_last_page:
                break
            page += 1
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")
            break

# Example usage:
api_url = 'https://vendor-api.jumia.com/catalog/products'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHNGFfV2tmeGRzSC0tVzJCUGRaclZuSmxFN1Zya29HaVRDUVVjczMxX2hFIn0.eyJqdGkiOiJkYWM5NTgxMS0zYWVkLTQ5ZTYtYjk3YS05Zjg1NTY4MjkxOTkiLCJleHAiOjE3MzMzNDA3ODUsIm5iZiI6MCwiaWF0IjoxNzMzMjk3NTg1LCJpc3MiOiJodHRwczovL3ZlbmRvci1hcGkuanVtaWEuY29tL2F1dGgvcmVhbG1zL2FjbCIsInN1YiI6ImY3YWExZmU3LTEwZGQtNGYxZS04N2M2LTk4MjJkZGU3ZmE4NiIsInR5cCI6IkJlYXJlciIsImF6cCI6IjRjM2QyZmZiLTE2NDQtNDc3NC05OWYzLWMzNDQxMzMyZjFkYiIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6Ijg3MmY3MzEzLTlkYjAtNDNhOS1iNGZkLTc1MTM1OTliMzZkMiIsImFjciI6IjEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InRzNHMtY2lAdGhlc2hvcDRzcG9ydC5jb20iLCJsb2NhbGUiOiJlbiIsImVtYWlsIjoidHM0cy1jaUB0aGVzaG9wNHNwb3J0LmNvbSJ9.LE76meIS4T_E8CcSTAhSaDn_qBVnFk7lec5m1x8YyNw7KLOeyzx3zfv1PfZzymyP6KjEM7sNJ8HfbaaUgHVwpn36z7dDvXS4oklUAV-e6dZJW7f7Dsto4vQ1tgjkZrU_6iOGl9LgEUjYlmeVS7I-g_sOzgDxpnGL4OiOEwzNPbSS9nZa4R9uba-Di5AzyV62en5rQyrS6sp33S7g9qiccl3crmSjRFQDYJpdVRxJz4Gji0aktXbHIWv6yzcb06YctghcUTGVdBhFdBo8F8d5424jichSnLknt1kozjeUUzJof_FG8JAe8d_HfBnEKdsgbmvXRn7tb4yX_Z10dKjBCA'
shop_id = 'bca4a0d7-8bcb-4e42-925c-380f83e225b0'
fetch_all_products(api_url, token, shop_id)
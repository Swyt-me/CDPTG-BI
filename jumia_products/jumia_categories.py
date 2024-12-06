import requests
import os
import time
import json

def fetch_categories(api_url, token, page):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f"{api_url}?page={page}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def save_to_file(data, page):
    folder_path = 'jumia_categories'
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'categories_page_{page}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def fetch_all_categories(api_url, token, total_pages):
    for page in range(1, total_pages + 1):
        try:
            categories = fetch_categories(api_url, token, page)
            save_to_file(categories, page)
            print(f"Page {page} fetched and saved.")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

# Example usage:
api_url = 'https://vendor-api.jumia.com/catalog/categories'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHNGFfV2tmeGRzSC0tVzJCUGRaclZuSmxFN1Zya29HaVRDUVVjczMxX2hFIn0.eyJqdGkiOiI1ODdlN2U3ZS03MzU0LTRiN2YtYjljYy1hNjZiZTdhODlmYzUiLCJleHAiOjE3Mjc5ODc3NjQsIm5iZiI6MCwiaWF0IjoxNzI3OTQ0NTY0LCJpc3MiOiJodHRwczovL3ZlbmRvci1hcGkuanVtaWEuY29tL2F1dGgvcmVhbG1zL2FjbCIsInN1YiI6ImUzZDFlMjc2LTNkMmItNDIzYi1hMzcyLTY3MDdhYmU3NGJlYSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImMxY2FmMjI4LTExMWQtNDYyZC1hNTk0LTI1OTk3MTJkOTE2YiIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjViMjQzZmJiLTU5NjctNDQ2Yy04MjA4LTZhMjZmYjk4OTk0NyIsImFjciI6IjEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJWaWN0b2lyZSBCb2huIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYS5zaGFpa2hAY3B0ZGcuY29tIiwiZ2l2ZW5fbmFtZSI6IlZpY3RvaXJlIiwibG9jYWxlIjoiZW4iLCJmYW1pbHlfbmFtZSI6IkJvaG4iLCJlbWFpbCI6ImEuc2hhaWtoQGNwdGRnLmNvbSJ9.UNSAfmxzK2u8B0jNyeH6_NqcQY5ZkCoSkMImu6Prr5VWO7C2P19b4SWxSFnRASkec4j7x9Xm5b-LpcHY2qAvhnc1hrcH8I0Jn7-IntZsXV0UY4ADVkH65cE7shVh5sFZQfkqZdslWRkQX9FNKXd7tCYJ-t038VvdRHSVj_sriwNHN4OmAlagK8-SFq9htK7v_YWPR_Ad8m2GnBNiHcc12cDtI3cacuEZ6nTyKIspNYJZdyA57mK39HqUdHUzcvF6IcquS9BW1n3KyaiLLtJbsx8X7QhGGdl_6nJxKtZZ5iVVuOE3GgPfNtgrpP1VLfKIhViKsLyJkwZYaVuAkKhCpw'
total_pages = 556
fetch_all_categories(api_url, token, total_pages)


def read_all_saved_files():
    folder_path = 'jumia_categories'
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                data = json.load(file)
                print(f"Data from {file_name}: {data}")

# Example usage:
read_all_saved_files()
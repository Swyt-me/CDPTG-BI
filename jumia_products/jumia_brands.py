import requests
import os
import time
import json

def fetch_brands(api_url, token, page):
    headers = {
        'Authorization': f'Bearer {token}',
        'Cookie': '__cf_bm=DUIs_RyJAhfrhNqX1UlfBqoWprabR_Q0tYO9itKTlho-1727957272-1.0.1.1-1mYGxX1YPZN3Kfgl15EmrdNuUqsS1TZhagI71wV6Qdk5E5Wi3wlEizFVEn3SA4Blf5W4jHKdReS77PvczSKGFQ'
    }
    response = requests.get(f"{api_url}?page={page}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def save_to_file(data, page):
    folder_path = 'jumia_brands'
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f'brands_page_{page}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def fetch_all_brands(api_url, token, total_pages):
    for page in range(1, total_pages + 1):
        try:
            brands = fetch_brands(api_url, token, page)
            save_to_file(brands, page)
            print(f"Page {page} fetched and saved.")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred on page {page}: {e}")

# Example usage:
api_url = 'https://vendor-api.jumia.com/catalog/brands'
token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJHNGFfV2tmeGRzSC0tVzJCUGRaclZuSmxFN1Zya29HaVRDUVVjczMxX2hFIn0.eyJqdGkiOiI3NzRlOGJlNS0wNjM5LTQ3OGYtYWVlZS0xM2RkNjdkYjlkMzEiLCJleHAiOjE3Mjc5ODgyNTYsIm5iZiI6MCwiaWF0IjoxNzI3OTQ1MDU2LCJpc3MiOiJodHRwczovL3ZlbmRvci1hcGkuanVtaWEuY29tL2F1dGgvcmVhbG1zL2FjbCIsInN1YiI6ImUzZDFlMjc2LTNkMmItNDIzYi1hMzcyLTY3MDdhYmU3NGJlYSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImMxY2FmMjI4LTExMWQtNDYyZC1hNTk0LTI1OTk3MTJkOTE2YiIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjViMjQzZmJiLTU5NjctNDQ2Yy04MjA4LTZhMjZmYjk4OTk0NyIsImFjciI6IjEiLCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm5hbWUiOiJWaWN0b2lyZSBCb2huIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiYS5zaGFpa2hAY3B0ZGcuY29tIiwiZ2l2ZW5fbmFtZSI6IlZpY3RvaXJlIiwibG9jYWxlIjoiZW4iLCJmYW1pbHlfbmFtZSI6IkJvaG4iLCJlbWFpbCI6ImEuc2hhaWtoQGNwdGRnLmNvbSJ9.Skg4mVM0krW151dPL4gzwB3LvYrF0NSfSHqSGHi3xrIod9K4YVmOJ7en7tWnNR3x4ghJb7rDZ8zWNrdYl6fymHfjfH7Ub2TtluwzhMc4iqnM0JZonpXb25_IxA-r1U1IDSCtcJSaMzoQtDksSj-ni3MdxBTPWax8Q6g1wJMJjGQUVuTaRI1d2TPhUnzLdKRkX7Rxr4J8dKheDY0Pd6gA-BjFGBH89P5oFy1n1SSskoSfHn1NAFyapDcnx_EjYNC9Espski4C9LneiP6q88MuwJjNaASLGnRFeKW6wr2R-sR8IYNd2j6tTBod60gjBFBYOnuX-vlpceKWbF6-ppj4YQ'
total_pages = 3417
fetch_all_brands(api_url, token, total_pages)
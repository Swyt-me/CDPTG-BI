import requests
import hashlib
import hmac
import time

# Environment variables extracted from Postman files
caller = "$apicaller"  # Your API Caller name
#caller = "Mojaa"  # Your API Caller name
merchant = "Mojaa"      # Merchant Account name
password = "hT790ffrMElo5H64"  # Your secret password (HMAC secret)

# Generate the HMAC signature
def generate_signature(caller, merchant, password, path, body=""):
    # Get the current Unix timestamp in seconds (must be in UTC)
    timestamp = str(int(time.time()))
    
    # Create the message by concatenating values in the specified order
    message = caller + merchant + timestamp + path + body
    
    # Create HMAC SHA256 signature and convert it to hexadecimal (uppercase)
    signature = hmac.new(password.encode(), message.encode(), hashlib.sha256).hexdigest().upper()
    
    return timestamp, signature

# API call for Healthcheck
def healthcheck():
    print("Performing Healthcheck...")

    # Healthcheck endpoint information
    healthcheck_path = "/api/v3/healthcheck"
    base_url = "https://payment-sandbox.payzone.ma"
    healthcheck_url = base_url + healthcheck_path

    # Generate the signature for healthcheck
    timestamp, signature = generate_signature(caller, merchant, password, healthcheck_path)

    # Set up the headers for the healthcheck request
    headers = {
        "X-MerchantAccount": merchant,
        "X-CallerName": caller,
        "X-HMAC-Timestamp": timestamp,
        "X-HMAC-Signature": signature,
        "Content-Type": "application/json"
    }

    # Make the GET request to the healthcheck endpoint
    try:
        response = requests.get(healthcheck_url, headers=headers)
        
        # Check for HTTP response status code
        if response.status_code == 200:
            print("Healthcheck successful!")
            print("Response data:", response.json())
        else:
            print(f"Healthcheck failed with status code {response.status_code}")
            print("Response message:", response.text)

    except Exception as e:
        print(f"An error occurred during healthcheck: {str(e)}")

# API call to retrieve transaction details
def get_transaction_details():
    print("Getting Transaction Details...")

    # Transaction details endpoint information
    base_url = "https://payment.payzone.ma/api/v3"
    path = "/charges"
    full_url = base_url + path

    # Generate the signature for transaction details
    timestamp, signature = generate_signature(caller, merchant, password, path)

    # Set up the headers for the API request
    headers = {
        "X-MerchantAccount": merchant,
        "X-CallerName": caller,
        "X-HMAC-Timestamp": timestamp,
        "X-HMAC-Signature": signature,
        "Content-Type": "application/json"
    }

    # Make the GET request to retrieve transaction details
    try:
        response = requests.get(full_url, headers=headers)
        
        # Check for HTTP response status code
        if response.status_code == 200:
            print("Request successful!")
            print("Response data:", response.json())
        else:
            print(f"Request failed with status code {response.status_code}")
            print("Response message:", response.text)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run healthcheck first
healthcheck()

# Then retrieve transaction details
get_transaction_details()

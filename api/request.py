import requests

data = {
    "id": "5a5c562e-4386-44ad-bf6f-bab91081781e",
    "plate_number": "7695-OOO",
    "car_make": "Ford",
    "car_year": 2012,
    "owner_name": "Stefen",
    "owner_address": "92834 Kim Unions\nPort Harryport, MD 61729",
    "owner_phone_number": "+1505698632",
    "subscription_status": "active",
    "subscription_start": None,
    "subscription_end": None,
    "balance": 100.0,
    "timestamp": "2023-03-03T14:37:49",
    "rate": 9.99
}

response = requests.post("http://0.0.0.0:8000/send_data", json=data)

print(response.status_code)
print(response.json())

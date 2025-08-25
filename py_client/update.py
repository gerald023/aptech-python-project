import requests


endpoint = "http://localhost:8000/api/products/5/update/";

data = {
    "title": "Hello my Nigga",
    "price": 450.99
}
get_response = requests.put(endpoint, json=data) #simulates a get request/


print(get_response.json());


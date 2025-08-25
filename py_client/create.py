import requests


endpoint = "http://localhost:8000/api/products/create_product/";

data = {
    "title": " this field is done",
    "price": 32.99
}

get_response = requests.post(endpoint, json=data) #simulates a post request/


print(get_response.json());


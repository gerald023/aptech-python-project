import requests


endpoint = "http://localhost:8000/api/products/50040405245/";

get_response = requests.get(endpoint) #simulates a get request/


print(get_response.json());
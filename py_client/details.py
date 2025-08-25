import requests


endpoint = "http://localhost:8000/api/products/5/";
method_endpoint = "http://localhost:8000/api/products/5/method_details/";

get_response = requests.get(endpoint) #simulates a get request/
method_response = requests.get(method_endpoint);

print(get_response.json());
print(method_response.json());
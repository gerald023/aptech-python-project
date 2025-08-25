import requests


endpoint = "http://localhost:8000/api/products/mixin_view/";
details_endpoint = "http://localhost:8000/api/products/1/mixin_details/";


data = {
    "title": "Mixin Class Request",
    "price": 270.99
}

get_response = requests.get(endpoint) #simulates a get request/
list_response = requests.get(details_endpoint);
post_response = requests.post(endpoint, json=data);

# print(get_response.json());
# print(list_response.json());
print(post_response.json());
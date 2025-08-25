import requests


# endpoint = "https://httpbin.org/anything"; #first endpoint that leads to dummy data.
endpoint = "http://localhost:8000/api/";
post_endpoint = "http://localhost:8000/api/add_products/"

get_response = requests.get(endpoint, params={"abc": 123}, json={"query": "Hello world"}) #simulates a get request/
post_response = requests.post(post_endpoint, json={"title": "Post Request", "content": "this is a request to add product", "price": "2730.50"})

# get_response = requests.get(endpoint, params={'abc': 123}, data={"query": "Hello world!"}) #passing a form data into the api call/

print(get_response.json()); #prints the response from the rest api call.
# print(get_response.text)
print(post_response.json());

# print(get_response.status_code) #getting the satus code of the request sent.


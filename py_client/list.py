import requests
from getpass import getpass;


auth_endpoint = "http://localhost:8000/api/auth/";
username = input("What is your username? \n")
password = getpass("What is your password? \n");

auth_response = requests.post(auth_endpoint, json={
    'username': username, "password": password
})

print(auth_response.json())

if auth_response.status_code == 200:
    token = auth_response.json()['token'];
    
    #this used the default Token keyword in the header.
    # headers = {
    #     'Authorization': f"Token {token}"
    # }
    #This uses the modified keyword 'Bearer'
    headers = {
        'Authorization': f"Bearer {token}"
    }
    endpoint = "http://localhost:8000/api/products/";
    all_in_one_endpoint = 'http://localhost:8000/api/products/alt_view/'


    data = {
        "title": " this field is a list api view creating product",
        "price": 32.99
    }

    post_response = requests.post(all_in_one_endpoint, json=data)
    get_response = requests.get(all_in_one_endpoint);
    list_view_get_response = requests.get(endpoint, headers=headers);
    list_view_post_response = requests.post(endpoint, headers=headers, json=data)



    # print(get_response.json());
    # print(post_response.json());
    print(list_view_get_response.json());
    print(list_view_post_response.json());

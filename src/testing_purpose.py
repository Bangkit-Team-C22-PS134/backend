import requests


BASE = "http://127.0.0.1:5000/"

data = {

    "name" : "third video",
    "likes" : 72,
    "views" : 829,
    "api_key" : "91ee4fa1-ea73-4b43-97ef-38ff055f97a8"

}

print(data["api_key"])
response = requests.post(BASE + "video/3", data )
print(response.json())
import requests
from json import dumps


if __name__ == "__main__" :

    BASE = "http://127.0.0.1:5000/"

    data = {
        "name" : "hypeeee",
        "views" : 9812,
        "likes" : 291,
        "api_key": "91ee4fa1-ea73-4b43-97ef-38ff055f97a8"
    }

    response = requests.get(BASE + "video/4")
    print(response.json())
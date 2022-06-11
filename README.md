# Circle Backend Microservices

## Installation
Clone this repository and import into your prefered working directory
```bash
git clone https://github.com/Bangkit-Team-C22-PS134/backend
```

## Python Environments
### Required Packages:
The following packages need to be installed in python env before we run the Notebook:
```
    Flask
    itsdangerous
    Jinja2
    MarkupSafe
    Werkzeug
    click
    colorama
    tensorflow
    flask_restful
    gunicorn
    tensorflow
    tensorflow_hub
    pandas
    numpy
    tensorflow-datasets
    tensorflow_recommenders
```

## Configuration
### API Key:
Change api key at `src/api_test.py` with the following info:
```
cred = credentials.Certificate("INSERT_KEY_HERE.json")
```

For docker environment , insert Api key as **OS Env variable** with the name `FIREBASE_KEY`


## Docker build
Simply build docker image in parent directory of this repository , and ship it using docker run

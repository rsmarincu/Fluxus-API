import requests
import json

url = "http://localhost:5006/"

payload = {
    "ttid": 1,
    "did": 42628,
    "target": "class",
    "session_id": 956213,
    "predict_file": open('row.csv', 'rb')
}


files = {'predict_file': open('row.csv', 'rb')}

r = requests.post(url,  json=payload)
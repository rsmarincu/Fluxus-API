import requests
import json

from random import randrange
from timeit import default_timer as timer

url_upload = "http://fluxusml.com/pandas/upload/"
url_compute = "http://0.0.0.0:5006/"

file_path = "dataset_time_4.csv"

url_ = "http://127.0.0.1:5001/upload/"


compute_params = {
    'did': '50',
    'ttid': '1',
    'target': 'Class',
    'session_id': '12432421',
    'predict': '["x", "x", "x", "x", "o", "o", "x", "o", "o"]'
}

file = open(file_path, 'rb')

files = {
    'file':file
}

# start = timer()
# res = requests.post(url_upload, files=files, timeout=7200)
# end = 0
# print(res)
# end = timer()
# result = end-start
# print(result)

start = timer()
res = requests.post(url_compute, data=compute_params)
print(res)
end = 0
end = timer()
result = end - start
print(result)
import requests
import json
from random import randrange
from timeit import default_timer as timer

url_upload = "http://fluxusml.com/pandas/upload/"
url_compute_azure = "http://fluxusml.com/compute/"
url_compute = "http://127.0.0.1:5006/"

#file_path = "dataset_time_10.csv"

url_ = "http://127.0.0.1:5001/upload/"

ttt = '["x","x","x","x","o","o","x","o","o"]'
diabetes = '[6,148,72,35,0,33.6,0.627,50]'
mushroom = '["x","s","n","t","p","f","c","n","k","e","e","s","s","w","w","p","w","o","p","k","s","u"]'
iris = '[5.1,3.5,1.4,0.2]'
vote = '["n","y","n","y","y","y","n","n","n","y","?","y","y","y","n","y"]'
heart = '[70,1,4,130,322,0,2,109,0,2.4,2,3,3]'
vehicle = '[83,36,54,119,57,6,128,53,18,125,143,238,139,82,6,3,179,183]'
wine = '[14.23,1.71,2.43,15.6,127,2.8,3.06,0.28,2.29,5.64,1.04,3.92,1065]'
ecoli = '[0.49,0.29,0.48,0.5,0.56,0.24,0.35]'

compute_params = {
    'did': '39',
    'ttid': '1',
    'target': 'class',
    'session_id': randrange(0,1000000),
    'predict': ecoli
}
print(compute_params)
# file = open(file_path, 'rb')

# files = {
#     'file':file
# }

# start = timer()
# res = requests.post(url_upload, files=files, timeout=7200)
# end = 0
# print(res)
# end = timer()
# result = end-start
# print(result)

start = timer()
res = requests.post(url_compute, data=compute_params)
print(res.json())
end = 0
end = timer()
result = end - start
print(result)
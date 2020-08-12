import time
import rediswq
import os
import json
import pathlib

try: 
  session_id = os.environ['SESSION_ID']
except KeyError:
  session_id = 'default'

q = rediswq.RedisWQ(
    name=session_id, 
    host="20.49.225.191",
    port="6379"
    )

output = {}

while not q.empty():
  item = q.lease(lease_secs=10, block=True, timeout=2) 
  if item is not None:
    itemstr = item.decode("utf-8")
    output[itemstr] = f"Worked on {itemstr}"
    time.sleep(10)
    q.complete(item)
  
print(json.dumps(output))
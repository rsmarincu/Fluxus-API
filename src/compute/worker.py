import time
import rediswq
import os
import json
import pathlib

q = rediswq.RedisWQ(
    name="temperature_job", 
    host="20.49.225.191",
    port="6379")


output = {}
print("started")
while not q.empty():
  item = q.lease(lease_secs=10, block=True, timeout=2) 
  if item is not None:
    itemstr = item.decode("utf-8")

    print("Working on " + itemstr)
    output[itemstr] = f"Worked on {itemstr}"
    time.sleep(10) # Put your actual work here instead of sleep.
    q.complete(item)

print(json.dumps(output))

print("Queue empty, exiting")


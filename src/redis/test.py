import redis

host = '20.49.225.191'
port = 6379

r = redis.StrictRedis(host=host, port=port)

files = [i for i in range(1, 7)]

print("current state is ", r.lrange('temperature_job', 0, -1))

print(files)
r.rpush('temperature_job', *files)

# # View items in queue
print(r.lrange('temperature_job', 0, -1))
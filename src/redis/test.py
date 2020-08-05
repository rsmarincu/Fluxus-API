import redis

host = '20.49.225.191'
port = 6379

r = redis.StrictRedis(host=host, port=port)
print(r)
files = [i for i in range(1, 7)]

# # Push filenames onto queue
r.rpush('temperature_job', *files)

# # View items in queue
print(r.lrange('temperature_job', 0, -1))
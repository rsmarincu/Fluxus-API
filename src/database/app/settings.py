from environs import Env


env = Env()


BIND_HOST = env('BIND_HOST', default='0.0.0.0')
BIND_PORT = env.int('BIND_PORT', default=5000)

NEO4J_HOST = env('NEO4J_HOST', default='51.11.6.65')
NEO4J_PORT = env.int('NEO4J_PORT', default=7687)
NEO4J_USER = env('NEO4J_USER', default='neo4j')
NEO4J_PASSWORD = env('NEO4J_PASSWORD', default='admin')
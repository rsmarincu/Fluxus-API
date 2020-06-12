from py2neo import Graph
from py2neo.ogm import GraphObject, Property, Related
from py2neo.data import walk
from app import settings
import random, math

graph = Graph(
    host=settings.NEO4J_HOST,
    port=settings.NEO4J_PORT,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD,
)

class BaseModel(GraphObject):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def all(self):
        return self.match(graph)

    def save(self):
        graph.push(self)

class Dataset(BaseModel):
    __primarykey__ = 'did'

    did = Property()
    name = Property()
    file_format = Property()

    connections = Related('Dataset', 'DISTANCE_FROM')

    def as_dict(self):
        return {
            'did': self.did,
            'name': self.name,
            'file_format': self.file_format
        }
    
    def fetch(self):
        dataset = self.match(graph, self.did).first()
        return dataset
    
    def add_connections(self, dataset, distance):
        self.connections.add(dataset, 
                            {
                                'distance': distance
                            })
        self.save()

    def get_connections(self):
        return self.connections
    
    def get_close_connections(self, distance):
        target = self.match(graph, self.did).first().__node__
        rels = graph.relationships.match({target, None}, "DISTANCE_FROM").where(f"_.distance <= {distance}").order_by("_.distance")
        connections = [Dataset.wrap(rel.start_node) if rel.start_node != target else Dataset.wrap(rel.end_node) for rel in rels]
        return connections
from py2neo import Graph
from py2neo.ogm import GraphObject, Property, Related
from py2neo.data import walk
from app import settings
from openml import datasets, flows, runs, tasks

import random, math


graph = Graph(
    host="51.132.245.212",
    http_port=7474,
    bolt=False
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
    tasks = Related('Task', 'TO_SOLVE')

    def __repr__(self):
        return f"Dataset ({self.name}, {self.did})"
    
    def __eq__(self, other):
        if isinstance(other, Dataset):
            return ((self.did == other.did) and (self.name == other.name))
        else:
            return False
    
    def __hash__(self):
        return hash(self.__repr__())

    def as_dict(self):
        return {
            'did': self.did,
            'name': self.name,
            'file_format': self.file_format,
        }
    
    def fetch(self):
        dataset = self.match(graph, self.did).first()
        return dataset
    
    def add_connections(self, dataset, distance):
        self.connections.add(
            dataset, 
            {
                'distance': distance
            }
        )
        self.save()

    def get_connections(self):
        return self.connections
    
    def get_close_connections(self, distance):
        target = self.match(graph, self.did).first().__node__
        rels = graph.relationships.match({target, None}, "DISTANCE_FROM").where(f"_.distance <= {distance}").order_by("_.distance")
        connections = [Dataset.wrap(rel.start_node) if rel.start_node != target else Dataset.wrap(rel.end_node) for rel in rels]
        return connections
    
    def add_task(self, task):
        self.tasks.add(task)
        self.save()
    
    def get_tasks(self):
        return self.tasks

    def get_similar_tasks(self, task_type_id):
        return [task for task in self.tasks if task.task_type_id == task_type_id]

    
class Task(BaseModel):
    __primarykey__ = "tid"

    tid = Property()
    task_type = Property()
    task_type_id = Property()
    target_feature = Property()
    evaluation_measures = Property()
    estimation_procedure = Property()
    
    evaluations = Related('Evaluation', 'SCORED')

    def __repr__(self):
        return f"Task ({self.tid}, {self.task_type})"
    
    def __eq__(self, other):
        if isinstance(other, Task):
            return ((self.tid == other.tid) and (self.task_type_id == other.task_type_id))
        else:
            return False
    
    def __hash__(self):
        return hash(self.__repr__())

    def as_dict(self):
        return {
            'tid': self.tid,
            'task_type': self.task_type,
            'task_type_id': self.task_type_id,
            'target_feature': self.target_feature,
            'evaluation_measures': self.evaluation_measures,
            'estimation_procedure': self.estimation_procedure
        }
    
    def fetch(self):
        task = self.match(graph, self.tid).first()
        return task
    
    def add_evaluation(self, evaluation, score):
        self.evaluations.add(evaluation, {
            'score': score
        })
        self.save()
    
    def get_task(self):
        task = tasks.get_task(self.tid)
        return task
    
    def get_evaluations(self, limit):
        target = self.match(graph, self.tid).first().__node__
        rels = graph.relationships.match({target, None}, "SCORED").order_by("_.score")
        connections = [Evaluation.wrap(rel.start_node) if rel.start_node != target else Evaluation.wrap(rel.end_node) for rel in rels]
        connections.reverse()
        return connections[:limit]

class Flow(BaseModel):
    __primarykey__ = 'fid'

    fid = Property()
    name = Property()
    description = Property()
    dependencies = Property()

    runs = Related('Run', 'RESULT')

    def __repr__(self):
        return f"Flow ({self.fid}, {self.name})"
    
    def __eq__(self, other):
        if isinstance(other, Flow):
            return ((self.fid == other.fid) and (self.name == other.name))
        else:
            return False
    
    def __hash__(self):
        return hash(self.__repr__())

    def as_dict(self):
        return {
            'fid': self.fid,
            'name': self.name,
            'description': self.description,
            'dependencies': self.dependencies,
        }
    
    def fetch(self):
        flow = self.match(graph, self.fid).first()
        return flow
    
    def get_flow(self):
        flow = flows.get_flow(self.fid)
        return flow
    
    def get_model(self):
        flow = flows.get_flow(self.fid)
        model = flow.model
        return model
    
    def get_parameters(self):
        flow = flows.get_flow(self.fid)
        parameters = flow.parameters
        return parameters
    
    def add_runs(self, run):
        self.runs.add(run)
        self.save()

class Evaluation(BaseModel):
    __primarykey__ = 'rid'

    rid = Property()
    accuracy = Property()
    setup_id = Property()
    flow_id = Property()
    flow_name = Property()

    def __repr__(self):
        return f"Evaluation ({self.rid}, {self.accuracy})"
    
    def __eq__(self, other):
        if isinstance(other, Evaluation):
            return ((self.rid == other.rid) and (self.accuracy == other.accuracy))
        else:
            return False
    
    def __hash__(self):
        return hash(self.__repr__())
        
    def as_dict(self):
        return {
            'rid': self.rid,
            'accuracy': self.accuracy,
            'setup_id': self.setup_id,
            'flow_id': self.flow_id,
            'flow_name': self.flow_name
        }
    
    def fetch(self):
        evaluation = self.match(graph, self.rid).first()
        return evaluation
    
    

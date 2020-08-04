import graphene
from app.neo4j.openml_model import Dataset, Task, Evaluation

class DatasetSchema(graphene.ObjectType):
    did = graphene.Int()
    name = graphene.String()
    file_format = graphene.String()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset = Dataset(did=self.did).fetch()

class TaskSchema(graphene.ObjectType):
    tid = graphene.Int()
    task_type = graphene.String()
    task_type_id = graphene.Int()
    target_feature = graphene.String()
    evaluation_measures = graphene.String()
    estimation_procedure = graphene.String()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task = Task(tid=self.tid).fetch()

class EvaluationSchema(graphene.ObjectType):
    rid = graphene.Int()
    accuracy = graphene.Float()
    setup_id = graphene.Int()
    flow_id = graphene.Int()
    flow_name = graphene.String()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task = Task(rid=self.rid).fetch()


class Query(graphene.ObjectType):
    dataset = graphene.Field(lambda: DatasetSchema, did=graphene.Int())
    datasets = graphene.List(lambda: DatasetSchema)
    close_connections = graphene.List(lambda:DatasetSchema, did=graphene.Int(), distance=graphene.Int())
    similar_tasks = graphene.List(lambda: TaskSchema, did=graphene.Int(), task_type_id=graphene.Int())
    evaluations = graphene.List(lambda: EvaluationSchema, tid=graphene.Int(), limit=graphene.Int())

    def resolve_dataset(self, info, did):
        dataset = Dataset(did=did).fetch()
        return DatasetSchema(**dataset.as_dict())
    
    def resolve_datasets(self, info):
        return [DatasetSchema(**dataset.as_dict()) for dataset in Dataset().all]
    
    def resolve_close_connections(self, info, **kwargs):
        did = kwargs.get('did')
        distance = kwargs.get('distance')
        target = Dataset(did=did).fetch()
        return target.get_close_connections(distance)
    
    def resolve_similar_tasks(self, info, **kwargs):
        did = kwargs.get('did')
        task_type_id = kwargs.get('task_type_id')
        dataset = Dataset(did=did).fetch()
        tasks = dataset.get_similar_tasks(task_type_id)
        return [TaskSchema(**task.as_dict()) for task in tasks]

    def resolve_evaluations(self, info, **kwargs):
        tid = kwargs.get('tid')
        limit = kwargs.get('limit')
        task = Task(tid=tid).fetch()
        return task.get_evaluations(limit)

schema = graphene.Schema(query=Query, auto_camelcase=False)
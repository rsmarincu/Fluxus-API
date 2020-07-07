import graphene
from app.neo4j.openml_model import Dataset

class DatasetSchema(graphene.ObjectType):
    did = graphene.Int()
    name = graphene.String()
    file_format = graphene.String()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dataset = Dataset(did=self.did).fetch()

class Query(graphene.ObjectType):
    dataset = graphene.Field(lambda: DatasetSchema, did=graphene.Int())
    datasets = graphene.List(lambda: DatasetSchema)
    close_connections = graphene.List(lambda:DatasetSchema, did=graphene.Int(), distance=graphene.Int())

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

schema = graphene.Schema(query=Query, auto_camelcase=False)
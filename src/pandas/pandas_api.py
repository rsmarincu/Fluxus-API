import json
import pandas as pd
import openml
import os

from datetime import datetime
from werkzeug.datastructures import FileStorage
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from flask import Flask, request, send_file, make_response
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from string import Template
from scipy.io.arff import loadarff

app = Flask(__name__)
CORS(app)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

transport = RequestsHTTPTransport(url="http://fluxusml.com/graphql/interface")
client = Client(transport=transport)

parser = reqparse.RequestParser()
parser.add_argument('file', type=FileStorage, location='files')
parser.add_argument('labels', type=str, action='append')
parser.add_argument('did', type=str)
parser.add_argument('index', type=int)


add_dataset = Template("""
mutation {
    add_dataset(did:$did) {
        dataset {
            did,
            name
        },
        ok
    }
}
""")

datasets = """
{
    datasets {
        did,
        name
    }
}
"""



class Hello(Resource):
    def get(self):
        return {"message":"Hello from the pandas endpoint!"}

class UploadDataset(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        name = os.path.splitext(file_.filename)[0]
        csvfile = pd.read_csv(file_.stream)
        md = openml.datasets.create_dataset(
            data=csvfile,
            name=name,
            description='test',
            creator='RM',
            contributor='None',
            language='English',
            licence='Free',
            attributes='auto',
            default_target_attribute=None,
            ignore_attribute=[],
            citation=None,
            collection_date=datetime.today().strftime('%Y-%m-%d')
            )
        dataset = md.publish()
        processed = False
        while not processed:
            try:         
                d = openml.datasets.get_dataset(dataset.dataset_id)
                qual = d.qualities
                processed = True
                print(qual)
            except openml.exceptions.OpenMLServerException as e:
                print("Processing...")

        print(add_dataset.substitute(did=dataset.dataset_id))

        dataset_ = client.execute(gql(add_dataset.substitute(did=dataset.dataset_id))) 

        return dataset_

class Labels(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        csvfile = pd.read_csv(file_.stream)
        labels = csvfile.columns.values.tolist()
        return labels

class Columns(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        labels = data['labels']
        csvfile = pd.read_csv(file_.stream)

        resp = make_response(csvfile[labels].to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"   
        return resp

class CountNaN(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        csvfile = pd.read_csv(file_.stream)
        nans = csvfile.isnull().sum(axis = 0).tolist()
        return sum(nans) 
    
class DropNaN(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        csvfile = pd.read_csv(file_.stream)
        dataset = csvfile.dropna()
        resp = make_response(dataset.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"   
        return resp 

class GetDatasets(Resource):
    def get(self):
        ds = client.execute(gql(datasets)) 
        return ds['datasets']

class LoadDataset(Resource):
    def get(self):
        data = parser.parse_args()
        did = data['did']
        dataset = openml.datasets.get_dataset(dataset_id=did, download_data=True)
        raw = loadarff(dataset.data_file)
        filename = f"{dataset.name}.csv"
        df = pd.DataFrame(raw[0])
        csv_file = df.to_csv(index=False)
        resp = make_response(csv_file)
        resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
        resp.headers["Content-Type"] = "text/csv"   
        return resp

class GetRow(Resource):
    def post(self):
        data = parser.parse_args()
        index = data['index']
        file_ = data['file']
        csvfile = pd.read_csv(file_.stream)
        row = csvfile.iloc[[index]]
        resp = make_response(row.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"

        return resp

class DropColumns(Resource):
    def post(self):
        data = parser.parse_args()
        file_ = data['file']
        labels = data['labels']

        csvfile = pd.read_csv(file_.stream)
        csvfile = csvfile.drop(labels, axis=1)

        resp = make_response(csvfile.to_csv(index=False))
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv" 

        return resp




api.add_resource(Hello,'/hello/')
api.add_resource(Labels,'/labels/')
api.add_resource(Columns,'/columns/')
api.add_resource(CountNaN,'/countnan/')
api.add_resource(DropNaN,'/dropnan/')
api.add_resource(UploadDataset,'/upload/')
api.add_resource(GetDatasets,'/datasets/')
api.add_resource(LoadDataset,'/load/')
api.add_resource(GetRow,'/row/')
api.add_resource(DropColumns,'/dropcolumns/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5001')

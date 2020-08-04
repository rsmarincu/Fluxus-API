from flask import Flask
from flask_restful import Resource, Api, reqparse
from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error

import openml
import subprocess
import sys
import re, os 
import importlib, site
import pickle
import pip


app = Flask(__name__)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

parser = reqparse.RequestParser()
parser.add_argument('flow', type=int, location='json')
parser.add_argument('task', type=int, location='json')

class Status(Resource):
    def get(self):
        return 200

class Compute(Resource):
    def post(self):
        args = parser.parse_args()
        print(args, file=sys.stdout)
        flowid = args['flow']
        taskid = args['task']

        flow = openml.flows.get_flow(flowid, reinstantiate=True, strict_version=False)
        task = openml.tasks.get_task(taskid)


        dataset = task.get_dataset()
        tti = task.task_type_id    
        ep = task.estimation_procedure_id
        em = task.evaluation_measure

        model = flow.model

        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format='array',
            target=dataset.default_target_attribute
        )

        model.fit(X, y)
        preds = model.predict(X)
        score = mean_squared_error(y, preds)

        return score

api.add_resource(Status,'/')
api.add_resource(Compute,'/compute/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="1234") 
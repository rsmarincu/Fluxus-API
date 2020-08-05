from flask import Flask
from flask_restful import Resource, Api, reqparse
from sklearn.metrics import roc_auc_score, accuracy_score

import requests
import openml
import subprocess
import sys
import re, os 
import importlib, site
import sklearn
import pip


app = Flask(__name__)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

parser = reqparse.RequestParser()
parser.add_argument('flow', type=int, location='json')
parser.add_argument('task', type=int, location='json')

def install(package):
    pip.main(['install', package])

def get_dependencies(dependencies):
    dependencies = dependencies.split('\n')
    to_install = {}
    print(dependencies, file=sys.stdout)

    dep_list = []
    
    for dependency in dependencies:
        parts = re.split('(>=|==|<=|_)', dependency)
        name = parts[0]
        if parts[1] in ['<=', '_', '==']:
            version = parts[2]
        elif parts[1] in ['>=']:
            version = 'latest'

        if name == 'sklearn' : 
            name = 'scikit-learn'
            version = 'latest'

        dep_list.append({
            'name':name,
            'version':version
        })
    
    return dep_list

class Load(Resource):
    def post(self):

        path = site.USER_SITE

        if path not in sys.path:
            sys.path.append(path)

        args = parser.parse_args()

        flowid = args['flow']
        taskid = args['task']

        task = openml.tasks.get_task(taskid)
        flow = openml.flows.get_flow(flowid)

        dependencies = get_dependencies(flow.dependencies)
        print(dependencies, file=sys.stdout)

        for dependency in dependencies:
            if dependency['version'] == 'latest':
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency['name']])
            else:
                to_install = dependency['name'] + '==' + dependency['version']
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', to_install])

        payload = {
                "flow":flowid,
                "task":taskid
            }
        headers = {
                'Content-Type': 'application/json'
            }
        
        url = "http://0.0.0.0:1234/"
        url_compute = "http://0.0.0.0:1234/compute/"
        score = None

        try:
            check = requests.get(url)
            score = requests.post(url_compute, headers=headers, json=payload)
        except:
            subprocess.Popen([sys.executable, '-u', 'script.py'])
        
        while score is None:
            try:
                score = requests.post(url_compute , headers=headers, json=payload)
            except:
                pass
            

        return score.json()
        
api.add_resource(Load,'/load/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5006") 
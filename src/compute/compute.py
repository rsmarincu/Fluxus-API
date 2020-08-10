from flask import Flask
from flask_restful import Resource, Api, reqparse
from sklearn.metrics import roc_auc_score, accuracy_score
from kubernetes import client, config, utils
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from string import Template

import requests
import openml
import subprocess
import sys
import re, os 
import importlib, site
import sklearn
import pip
import json
import yaml
import rediswq

app = Flask(__name__)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

parser = reqparse.RequestParser()
parser.add_argument('did', type=int, location='json')
parser.add_argument('tid', type=int, location='json')
parser.add_argument('session_id', type=str, location='json')

transport = RequestsHTTPTransport("http://fluxusml.com/graphql/interface")
client = Client(transport=transport)

close_connections = Template("""
{
    close_connections(did:$did, distance:$distance) {
        did
        name
    }
}
""")

similar_tasks = Template("""
{
    similar_tasks(did:$did,task_type_id:$task_type_id) {
        tid
    }
}
""")

evaluations = Template("""
{
    evaluations(tid:$tid, limit:$limit)
}
""")

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

def set_jobs(number):
    file_path = 'job.yaml'
    with open (file_path) as f:
        job_file = yaml.load(f)
    
    job_file['spec']['parallelism'] = number

    with open (file_path, 'w') as f:
        yaml.dump(job_file, f)

def create_job():
    api = client.ApiClient()
    namespace = 'default'
    file_path = 'job.yaml'
    
    try:     
        utils.create_from_yaml(api, file_path, namespace=namespace)
    except utils.FailToCreateError as e:
        print("already exists")


    batch = client.BatchV1Api()
    job = batch.read_namespaced_job(name="job-wq-2", namespace=namespace)
    controller_uid = job.metadata.labels["controller-uid"]

    core = client.CoreV1Api()

    pod_label_selector = "controller-uid=" + controller_uid
    pods_list = core.list_namespaced_pod(namespace=namespace, label_selector=pod_label_selector)
    pod = pods_list.items[0].metadata.name

    try:
        pod_log_response = core.read_namespaced_pod_log(name=pod, namespace=namespace, _return_http_data_only=True, _preload_content=False)
        pod_log = pod_log_response.data.decode("utf-8")
        data = json.loads(pod_log)
        return data
    except client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)

class Load(Resource):
    def post(self):

        path = site.USER_SITE

        if path not in sys.path:
            sys.path.append(path)

        args = parser.parse_args()

        tid = args['tid']
        did = args['did']
        session_id = args['session_id']

        task = openml.tasks.get_task(tid)

        print(task.task_type_id)
        redis = rediswq.RedisWQ(
            name=session_id, 
            host="20.49.225.191",
            port="6379")

        datasets = client.execute(gql(close_connections.substitute(did=did, distance=1000)))
       
        for dataset in datasets['close_connections']:
            tasks = client.execute(gql(similar_tasks.substitute(
                did=dataset['did'],
                task_type_id=task.task_type_id
            )))
            print(tasks)



        # for dependency in dependencies:
        #     if dependency['version'] == 'latest':
        #         subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency['name']])
        #     else:
        #         to_install = dependency['name'] + '==' + dependency['version']
        #         subprocess.check_call([sys.executable, '-m', 'pip', 'install', to_install])

        # payload = {
        #         "flow":flowid,
        #         "task":taskid
        #     }
        # headers = {
        #         'Content-Type': 'application/json'
        #     }
        
        # url = "http://0.0.0.0:1234/"
        # url_compute = "http://0.0.0.0:1234/compute/"
        # score = None

        # try:
        #     check = requests.get(url)
        #     score = requests.post(url_compute, headers=headers, json=payload)
        # except:
        #     subprocess.Popen([sys.executable, '-u', 'script.py'])
        
        # while score is None:
        #     try:
        #         score = requests.post(url_compute , headers=headers, json=payload)
        #     except:
        #         pass
            

        # return score.json()
        
api.add_resource(Load,'/load/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5006") 
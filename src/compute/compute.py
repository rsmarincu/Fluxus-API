from flask import Flask
from flask_restful import Resource, Api, reqparse
from kubernetes import config, utils, watch
from kubernetes import client as kclient
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from string import Template

import requests
import openml
import subprocess
import sys
import re, os 
import importlib, site
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
    evaluations(tid:$tid, limit:$limit) {
        rid,
        accuracy,
        flow_id,
        flow_name
    }
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

def set_jobs(number, session_id):
    file_path = 'job.yaml'
    with open (file_path) as f:
        job_file = yaml.load(f)
    
    job_file['spec']['parallelism'] = number
    job_file['spec']['template']['spec']['containers'][0]['env'][1]['value'] = session_id

    with open (file_path, 'w') as f:
        yaml.dump(job_file, f)

def create_job(size):
    config.load_kube_config()
    api = kclient.ApiClient()
    core = kclient.CoreV1Api()

    namespace = 'default'
    file_path = 'job.yaml'
    
    try:     
        utils.create_from_yaml(api, file_path, namespace=namespace)
    except utils.FailToCreateError as e:
        print("already exists")


    batch = kclient.BatchV1Api()
    job = batch.read_namespaced_job(name="job-wq-2", namespace=namespace)
    controller_uid = job.metadata.labels["controller-uid"]

    pod_label_selector = "controller-uid=" + controller_uid
    pods_list = core.list_namespaced_pod(namespace=namespace, label_selector=pod_label_selector)
    pods = pods_list.items
    results = []

    w = watch.Watch()

    while True:
        for event in w.stream(
            func=core.list_namespaced_pod,
            label_selector=pod_label_selector,
            namespace=namespace,
            timeout_seconds=60):
            if event['object'].status.phase == "Succeeded":
                pod = event['object'].metadata.name
                pod_log_response = core.read_namespaced_pod_log(name=pod, namespace=namespace, _return_http_data_only=True, _preload_content=False)
                pod_log = pod_log_response.data
                data = json.loads(pod_log)
                results.append(data)
                if len(results) == size:
                    w.stop()
                    return results

def delete_job(name):
    config.load_kube_config()

    api = kclient.BatchV1Api()
    api.delete_namespaced_job(
        name=name,
        namespace='default'
    )   

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

        redis = rediswq.RedisWQ(
            name=session_id, 
            host="20.49.225.191",
            port="6379")

        datasets = client.execute(gql(close_connections.substitute(did=did, distance=1000)))
        tasks_to_check = set()

        for dataset in datasets['close_connections']:
            tasks = client.execute(gql(similar_tasks.substitute(
                did=dataset['did'],
                task_type_id=task.task_type_id
            )))
            for t in tasks['similar_tasks']:     
                tasks_to_check.add(t['tid'])

        flows = set()

        for tid in tasks_to_check:
            evals = client.execute(gql(evaluations.substitute(
                tid=tid,
                limit=1
            )))
            for e in evals['evaluations']:
                flows.add(e['flow_id'])

        jobs = len(flows)
        redis.add_items(list(flows), str(session_id))
        set_jobs(jobs, session_id)
        results = create_job(jobs)
        delete_job("job-wq-2")
        return results


    
api.add_resource(Load,'/load/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5006") 
from flask import Flask
from flask_restful import Resource, Api, reqparse
from kubernetes import config, utils, watch
from kubernetes import client as kclient
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from string import Template
from flask_cors import CORS
from xml.etree import ElementTree as ET

from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn import compose, ensemble, impute, neighbors, preprocessing

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
import itertools
import pickle
import pandas as pd 

app = Flask(__name__)
CORS(app)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

parser = reqparse.RequestParser()

parser.add_argument('did', type=int, location='json')
parser.add_argument('ttid', type=int, location='json')
parser.add_argument('session_id', type=str, location='json')

parser.add_argument('task_type_id', type=int, location='json')
parser.add_argument('did', type=int, location='json')
parser.add_argument('target', type=str, location='json')
parser.add_argument('predict', type=list, location='json')



active = []
active_datasets = []


transport = RequestsHTTPTransport("http://fluxusml.com/graphql/interface")
client = Client(transport=transport)

create_task_xml = Template("""
<oml:task_inputs xmlns:oml="http://openml.org/openml">
<oml:task_type_id>$ttid</oml:task_type_id>
<oml:input name="source_data">$did</oml:input>
<oml:input name="target_feature">$target</oml:input>
<oml:input name="estimation_procedure">$estimation</oml:input>
<oml:input name="evaluation_measures">$evaluation/oml:input>
</oml:task_inputs>
""")

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

def format_test(dataset, test, attribute_names):
    df = pd.DataFrame([test])
    df.columns = attribute_names

    dataset = dataset.append(df.loc[0], ignore_index=True)
    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        if dataset.dtypes[i] == 'object':
            dataset[label] = le.fit_transform(dataset[label])

    row = dataset.tail(1)

    return row

def create_model(fid, did, target):
    flow = openml.flows.get_flow(fid, reinstantiate=True, strict_version=False)
    dataset = openml.datasets.get_dataset(did)

    model = flow.model

    X, y, categorical_indicator, attribute_names = dataset.get_data(
        dataset_format='dataframe',
        target=target
    )

    X[target] = y
    X = X.dropna()

    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        if X.dtypes[i] == 'object':
            X[label] = le.fit_transform(X[label])


    y = X[target]
    X = X.drop([target], axis=1)

    model.fit(X, y)
    filename = f"f{fid}-d{did}.pkl"

    with open (filename, 'wb') as f:
        pickle.dump(model, f)

    
    return filename

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

def set_jobs(number, session_id, ):
    file_path = 'job.yaml'
    with open (file_path) as f:
        job_file = yaml.load(f)
    
    job_file['spec']['parallelism'] = number
    job_file['spec']['completions'] = number
    job_file['spec']['template']['spec']['containers'][0]['env'][1]['value'] = session_id

    with open (file_path, 'w') as f:
        yaml.dump(job_file, f)

def create_job(size):
    #config.load_kube_config()
    config.load_incluster_config()
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
    finished_pods = []
    w = watch.Watch()

    while True:
        for event in w.stream(
            func=core.list_namespaced_pod,
            label_selector=pod_label_selector,
            namespace=namespace,
            timeout_seconds=30):
            print(event['object'].status.phase)
            if event['object'].status.phase in ["Succeeded", "Terminating"]:
                try:
                    pod = event['object'].metadata.name
                    if pod not in finished_pods:
                        pod_log_response = core.read_namespaced_pod_log(name=pod, namespace=namespace, _return_http_data_only=True, _preload_content=False)
                        pod_log = pod_log_response.data
                        data = json.loads(pod_log)
                        finished_pods.append(pod)
                except kclient.rest.ApiException as e:
                    print(e)
                    pod = event['object'].metadata.name
                    data = {
                        'flow': None,
                        'target': None,
                        'score': None 
                    }
                    finished_pods.append(pod)
                if data not in results:
                    results.append(data)
                if len(finished_pods) == size:
                    w.stop()
                    return results



def delete_job(name):
    #config.load_kube_config()
    config.load_incluster_config()
    body = kclient.V1DeleteOptions(propagation_policy='Background')
    api = kclient.BatchV1Api()
    api.delete_namespaced_job(
        name=name,
        body=body,
        namespace='default'
    )   

class Load(Resource):
    def post(self):

        path = site.USER_SITE

        if path not in sys.path:
            sys.path.append(path)

        args = parser.parse_args()

        ttid = args['ttid']
        did = args['did']
        target = args['target']
        session_id = args['session_id']
        predict = args['predict']

        print(f"Args: ttid:{ttid}, did:{did}, target:{target}, session_id:{session_id}, predict:{predict}")

        if did in active_datasets:
            
            result = filter(lambda dict: dict['did'] == did, active)
            print(result)
            result = list(result)[0]
            fid = result['flow']
            filename = f"f{fid}-d{did}.pkl"
            dataset = openml.datasets.get_dataset(did)

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            X[target] = y
            X = X.dropna()

            model = None

            with open(filename, 'rb') as f:
                model = pickle.load(f)

            test = format_test(X, predict, attribute_names)
            test = test.drop([target], axis=1)
            pred = model.predict(test)

            res = {
                target: pred.tolist()
            }

            return res

        else:
            redis = rediswq.RedisWQ(
                name=session_id, 
                host="20.49.225.191",
                port="6379")

            datasets = client.execute(gql(close_connections.substitute(did=did, distance=10000)))
            tasks_to_check = set()

            for dataset in datasets['close_connections']:
                tasks = client.execute(gql(similar_tasks.substitute(
                    did=dataset['did'],
                    task_type_id=ttid
                )))
                for t in tasks['similar_tasks']:     
                    tasks_to_check.add(t['tid'])

            flows = set()

            for t in tasks_to_check:
                evals = client.execute(gql(evaluations.substitute(
                    tid=t,
                    limit=1
                )))
                for e in evals['evaluations']:
                    flows.add(e['flow_id'])


            jobs = len(flows)
        
            items = zip(list(flows), itertools.repeat(did), itertools.repeat(target))

            print(list(flows))

            pickled = [pickle.dumps(t) for t in list(items)]
            redis.add_items(pickled, str(session_id))
            set_jobs(jobs, session_id)
            results = create_job(jobs)
            
            max_ = 1
            top = {}

            for result in results:
                if result['flow'] is not None:
                    if result['score']  < max_ and result['score'] > 0:
                        max_ = result['score']
                        top = result

            delete_job("job-wq-2")
            dataset = openml.datasets.get_dataset(did)

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            test = format_test(X, predict, attribute_names)

            X[target] = y

            X = X.dropna()
            file_ = create_model(top['flow'], did, target)
            model = None

            with open(file_, 'rb') as f:
                model = pickle.load(f)

            pred = model.predict(test)

            res = {
                target: pred.tolist()
            }

            active.append(top)
            active_datasets.append(did)

            return res

api.add_resource(Load,'/load/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5006", debug=True) 
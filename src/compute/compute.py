from flask import Flask
from flask_restful import Resource, Api, reqparse
from kubernetes import config, utils, watch
from kubernetes import client as kclient
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from string import Template
from flask_cors import CORS
from xml.etree import ElementTree as ET
from werkzeug.datastructures import FileStorage

from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn import compose, ensemble, impute, neighbors, preprocessing
from sklearn.model_selection import train_test_split
from timeit import default_timer as timer

import requests
import openml
import subprocess
import sys
import re, os 
import pip
import json
import yaml
import rediswq
import itertools
import pickle
import pandas as pd 
import warnings
import numpy as np

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)
api = Api(app)

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

parser = reqparse.RequestParser()

parser.add_argument('predict_file', type=FileStorage, location='files')
parser.add_argument('did', location='form')
parser.add_argument('ttid', location='form')
parser.add_argument('target', location='form')
parser.add_argument('session_id', location='form')
parser.add_argument('predict', location='form')

active = []
active_datasets = []

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

def format_string_row(dataset, test, attribute_names):
    df = pd.DataFrame([test])
    df.columns = attribute_names

    dataset = dataset.append(df.loc[0], ignore_index=True)
    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        print(label)
        if dataset.dtypes[i] not in ['float64', 'float', 'int']:
            try:
                dataset[label] = le.fit_transform(dataset[label])
            except TypeError as e:
                dataset = dataset.apply(dataset.to_numeric,args=('coerce'))
                dataset.dropna()
                dataset[label] = le.fit_transform(dataset[label])
    row = dataset.tail(1)

    return row

def format_row(dataset, test, attribute_names):
    df = pd.DataFrame(test)
    df.columns = attribute_names
    index = test.index
    len_rows = len(index)
    dataset = dataset.append(df.loc[0], ignore_index=True)
    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        if dataset.dtypes[i] not in ['float64', 'int']:
            try:
                dataset[label] = le.fit_transform(dataset[label])
            except TypeError as e:
                dataset = dataset.to_numeric(dataset[label], errors='coerce')
                dataset.dropna()
                dataset[label] = le.fit_transform(dataset[label])

    row = dataset.tail(len_rows)
    return row

def create_model(flow_id, dataset_id, target):
    try:
        flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
        dataset = openml.datasets.get_dataset(dataset_id)
        le = preprocessing.LabelEncoder()
        model = flow.model

        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format='dataframe',
            target=target
        )
        print(model)
        X[target] = y
        X = X.dropna()
        attribute_names.append(target)

        for i, label in enumerate(attribute_names):
            if X.dtypes[i] not in ['float64', 'int']:
                X[label] = le.fit_transform(X[label])

        y = X[target]
        X = X.drop([target], axis=1)


        X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33, random_state=42)

        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        score = accuracy_score(y_test, preds)

    except ValueError as e:
        if str(e) == "n_estimators must be an integer, got <class 'str'>.":
            flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
            dataset = openml.datasets.get_dataset(dataset_id)

            model = flow.model

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            X[target] = y
            X = X.dropna()

            le = preprocessing.LabelEncoder()
            labels = X.columns.values.tolist()

            for i, label in enumerate(labels):
                if X.dtypes[i] == 'object':
                    X[label] = le.fit_transform(X[label])


            y = X[target]
            X = X.drop([target], axis=1)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
            model.set_params(estimator__n_estimators=10)

            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = accuracy_score(y_test, preds)

        elif str(e) == '''value 0 for Parameter num_class should be greater equal to 1\nnum_class: Number of output class in the multi-class classification.''':
            flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
            dataset = openml.datasets.get_dataset(dataset_id)
            le = preprocessing.LabelEncoder()
            model = flow.model

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            X[target] = y
            num_classes = len(X[target].unique())

            X = X.dropna()
            attribute_names.append(target)

            for i, label in enumerate(attribute_names):
                if X.dtypes[i] not in ['float64', 'int']:
                    X[label] = le.fit_transform(X[label])

            y = X[target]
            X = X.drop([target], axis=1)

            X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33, random_state=42)

            model.set_params(estimator__num_class=num_classes)
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            score = accuracy_score(y_test, preds)

    except TypeError as e:
        flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
        dataset = openml.datasets.get_dataset(dataset_id)

        model = flow.model

        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format='dataframe',
            target=target
        )

        X[target] = y
        X = X.dropna()

        le = preprocessing.LabelEncoder()
        labels = X.columns.values.tolist()
        attribute_names.append(target)

        for i, label in enumerate(attribute_names):
            if X.dtypes[i] not in ['float64', 'int']:
                X[label] = le.fit_transform(X[label])


        y = X[target]
        X = X.drop([target], axis=1)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        score = accuracy_score(y_test, preds)


    filename = f"f{flow_id}-d{dataset_id}.pkl"

    with open (filename, 'wb') as f:
        pickle.dump(model, f)

    
    return filename

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
    config.load_kube_config()
    #config.load_incluster_config()
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
    start = timer()
    max_ = 0
    top = {}
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
                        logs = pod_log.decode("utf-8").split('\n')
                        logs = logs[-2]
                        data = json.loads(logs)
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
                    for result in results:
                        if result['flow'] is not None:
                            if result['score']  > max_ and result['score'] < 1:
                                max_ = result['score']                               
                                top = result
                                now = timer()
                                elapsed = now - start
                                if max_ > 0.9 or (elapsed > 120 and top['flow'] is not None):
                                    w.stop()
                                    print("Found max or spent too much time")
                                    return top
                    
                if len(finished_pods) == size:
                    w.stop()
                    for result in results:
                        if result['flow'] is not None:
                            if result['score']  > max_ and result['score'] < 1:
                                max_ = result['score']                               
                                top = result
                    return top



def delete_job(name):
    config.load_kube_config()
    #config.load_incluster_config()
    body = kclient.V1DeleteOptions(propagation_policy='Background')
    api = kclient.BatchV1Api()
    api.delete_namespaced_job(
        name=name,
        body=body,
        namespace='default'
    )   

class Load(Resource):
    def post(self):

        args = parser.parse_args()
        ttid = args['ttid']
        did = args['did']
        target = args['target']
        session_id = args['session_id']
        predict = args['predict']
        predict_file = args['predict_file']

        is_csv = False


        if (isinstance(predict_file, FileStorage)):
            csvfile = pd.read_csv(predict_file.stream)
            predict = csvfile
            is_csv = True
        else:
            predict = json.loads(predict)

        print(f"Did: {did}, ttid: {ttid}, target: {target}, predict: {predict}, session_id: {session_id}")

        if (did, target) in active_datasets:
            print("Already exists.")
            result = filter(lambda dict: dict['did'] == did, active)
            result = list(result)[0]
            fid = result['flow']
            filename = f"f{fid}-d{did}.pkl"
            dataset = openml.datasets.get_dataset(did)

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            X = X.dropna()

            if is_csv:
                to_predict = format_row(X, predict, attribute_names)
            else:
                to_predict = format_string_row(X, predict, attribute_names)

            model = None

            with open(filename, 'rb') as f:
                model = pickle.load(f)

            pred = model.predict(to_predict)
            le = preprocessing.LabelEncoder()
            le.fit_transform(y)

            res = {
                target: list(le.inverse_transform(pred))
            }

            return res

        else:
            print("New dataset.")

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

            print(flows)
            jobs = len(flows)
            items = zip(list(flows), itertools.repeat(did), itertools.repeat(target))

            pickled = [pickle.dumps(t) for t in list(items)]
            redis.add_items(pickled, str(session_id))
            set_jobs(jobs, session_id)
            top = create_job(jobs)
            delete_job("job-wq-2")

            dataset = openml.datasets.get_dataset(did)

            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format='dataframe',
                target=target
            )

            X = X.replace(to_replace="?", value=np.nan)
            X = X.dropna()



            if is_csv:
                to_predict = format_row(X, predict, attribute_names)
            else:
                to_predict = format_string_row(X, predict, attribute_names)

            file_ = create_model(top['flow'], did, target)
            model = None

            with open(file_, 'rb') as f:
                model = pickle.load(f)

            pred = model.predict(to_predict)
            le = preprocessing.LabelEncoder()
            le.fit_transform(y)

            res = {
                target: list(le.inverse_transform(pred))
            }

            active.append(top)
            active_datasets.append((did, target))

            return res

api.add_resource(Load,'/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="5006", debug=True) 
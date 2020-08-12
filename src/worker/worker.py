import time
import rediswq
import os
import json
import pathlib
import sklearn
import openml
import pickle

from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

try: 
  session_id = os.environ['SESSION_ID']
except KeyError:
  session_id = 'default'

q = rediswq.RedisWQ(
    name=session_id, 
    host="20.49.225.191",
    port="6379"
    )


item = q.lease(lease_secs=50, block=True, timeout=2) 

if item is not None:
    tuple_ = pickle.loads(item)
    flow_id = tuple_[0]
    task_id = tuple_[1]

    try:
        flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
    except ModuleNotFoundError:
        q.complete(item)
        result = {
            'flow': flow_id,
            'task': task_id,
            'score': 100
        }
    
    task = openml.tasks.get_task(task_id)

    dataset = task.get_dataset()

    model = flow.model

    X, y, categorical_indicator, attribute_names = dataset.get_data(
        dataset_format='array',
        target=dataset.default_target_attribute
    )

    model.fit(X, y)
    preds = model.predict(X)
    score = mean_squared_error(y, preds)

    result = {
        'flow': flow_id,
        'task': task_id,
        'score': score
    }
    q.complete(item)

    
print(json.dumps(result))
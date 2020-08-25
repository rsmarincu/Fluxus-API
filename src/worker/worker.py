import time
import rediswq
import os
import json
import pathlib
import sklearn
import openml
import pickle
import pandas as pd 
import math

from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn import compose, ensemble, impute, neighbors, preprocessing

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


item = q.lease(lease_secs=500, block=True, timeout=None) 


if item is not None:
    tuple_ = pickle.loads(item)
    flow_id = tuple_[0]
    dataset_id = tuple_[1]
    target = tuple_[2]
    le = preprocessing.LabelEncoder()

    result = {
        'flow': flow_id,
        'target': target,
        'score': math.inf,
        'did': dataset_id
    }


    try:
        flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
        dataset = openml.datasets.get_dataset(dataset_id)

        model = flow.model

        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format='dataframe',
            target=target
        )

        X[target] = y
        X = X.dropna()


        for i, label in enumerate(attribute_names):
            if X.dtypes[i] == 'object':
                X[label] = le.fit_transform(X[label])


        y = X[target]
        X = X.drop([target], axis=1)

        model.fit(X, y)
        preds = model.predict(X)
        score = mean_squared_error(y, preds)

        result = {
            'flow': flow_id,
            'target': target,
            'score': score,
            'did': dataset_id
            }

        q.complete(item)

    except ModuleNotFoundError as e:
        result = {
            'flow': flow_id,
            'target': target,
            'score': math.inf,
            'did': dataset_id
        }
        q.complete(item)

    except ValueError as e:
        result = {
            'flow': flow_id,
            'target': target,
            'score': math.inf,
            'did': dataset_id
        }
        q.complete(item)

    except TypeError as e:
        result = {
            'flow': flow_id,
            'target': target,
            'score': math.inf,
            'did': dataset_id
        }
        q.complete(item)

    finally:
        q.complete(item)

    
print(json.dumps(result))
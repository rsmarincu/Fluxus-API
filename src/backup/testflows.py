
import os
import json
import pathlib
import sklearn
import openml
import pickle
import pandas as  pd 
from ast import literal_eval

from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn import compose, ensemble, impute, neighbors, preprocessing

openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

flow_id = 17488
dataset_id = 42628
target = "class"



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
    t = ["<0", 6,"critical/other existing credit", "radio/tv", 1169, "no known savings", ">=7", 4, "male single", "none", 4, "real estate", 67, "none", "own", 2, "skilled", 1, "yes", "yes"]

    test = pd.DataFrame([t])

    test.columns = attribute_names


    y = X[target]
    X = X.drop([target], axis=1)

    model.fit(X, y)
    preds = model.predict(X)

    score = mean_squared_error(y, preds)
    p = model.predict(test)

    print(p)

    result = {
        'flow': flow_id,
        'target': target,
        'score': score
        }



except ModuleNotFoundError as e:
    result = {
        'flow': flow_id,
        'target': target,
        'score': str(e)
    }
except ValueError as e:
    print("In value")
    flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
    dataset = openml.datasets.get_dataset(dataset_id)

    model = flow.model

    X, y, categorical_indicator, attribute_names = dataset.get_data(
        dataset_format='dataframe',
        target=target
    )

    t = ["<0", 6,"critical/other existing credit", "radio/tv", 1169, "no known savings", ">=7", 4, "male single", "none", 4, "real estate", 67, "none", "own", 2, "skilled", 1, "yes", "yes"]

    test = format_test(X, t, attribute_names)

    X[target] = y
    X = X.dropna()


    le = preprocessing.LabelEncoder()
    labels = X.columns.values.tolist()

    for i, label in enumerate(labels):
        if X.dtypes[i] == 'object':
            X[label] = le.fit_transform(X[label])


    y = X[target]
    X = X.drop([target], axis=1)

    model.fit(X, y)
    preds = model.predict(X)

    score = mean_squared_error(y, preds)
    # p = model.predict(test)

    #print(p)

    result = {
        'flow': flow_id,
        'target': target,
        'score': score
        }
    print(result)

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
    t = ["<0", 6,"critical/other existing credit", "radio/tv", 1169, "no known savings", ">=7", 4, "male single", "none", 4, "real estate", 67, "none", "own", 2, "skilled", 1, "yes", "yes", "good"]
    test = format_test(X, t)
    test = test.drop([target], axis=1)
    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        if X.dtypes[i] == 'object':
            X[label] = le.fit_transform(X[label])


    y = X[target]
    X = X.drop([target], axis=1)

    model.fit(X, y)
    preds = model.predict(X)

    score = mean_squared_error(y, preds)
    p = model.predict(test)

    print(p)

    result = {
        'flow': flow_id,
        'target': target,
        'score': score
        }

    print(result)

finally:
    result = {
        'flow': flow_id,
        'target': target,
        'score': "ERROR"
        }
    print (result)





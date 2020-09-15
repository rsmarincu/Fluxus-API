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
import pprint

from warnings import simplefilter
from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn import compose, ensemble, impute, neighbors, preprocessing
from sklearn.model_selection import train_test_split

simplefilter(action='ignore', category=FutureWarning)

pp = pprint.PrettyPrinter(indent=4)


openml.config.apikey = '451234759bbada8dfaeb365266da9735'
openml.config.server = 'https://www.openml.org/api/v1'
openml.config.set_cache_directory(os.path.expanduser('~/.openml/cache'))

def format_string_row(dataset, test, attribute_names):
    df = pd.DataFrame([test])
    df.columns = attribute_names
    dataset = dataset.append(df.loc[0], ignore_index=True)
    le = preprocessing.LabelEncoder()

    for i, label in enumerate(attribute_names):
        if dataset.dtypes[i] not in ['float64', 'float', 'int']:
            try:
                dataset[label] = le.fit_transform(dataset[label])
            except TypeError as e:
                dataset[label] = dataset[label].apply(int)
                dataset[label] = le.fit_transform(dataset[label])

    row = dataset.tail(1)

    return row

flow_id = 5804
target = "chol"
dataset_id = 204
predict = [63, 1, 1, 145, 1, 2, 150, 0, 2.3, 3, 0, 6, 0]

result = {
    'flow': flow_id,
    'target': target,
    'score': math.inf,
    'did': dataset_id,
}

try:
    flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
    dataset = openml.datasets.get_dataset(dataset_id)
    le = preprocessing.LabelEncoder()
    model = flow.model

    X, y, categorical_indicator, attribute_names = dataset.get_data(
        dataset_format='dataframe',
        target=target
    )

    X[target] = y
    X = X.dropna()

    to_predict = format_string_row(X, predict, attribute_names)

    backup = attribute_names

    attribute_names.append(target)

    for i, label in enumerate(attribute_names):
        if X.dtypes[i] not in ['float64', 'int']:
            X[label] = le.fit_transform(X[label])


    y = X[target]

    X = X.drop([target], axis=1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    try:
        score = accuracy_score(y_test, preds)
    except Exception as e:
        score = mean_squared_error(y_test, preds)
    
    print(score)
    print(preds)

    preds_labels = le.inverse_transform(preds)


    p = model.predict(to_predict)
    result = {
        'flow': flow_id,
        'target': target,
        'score': score,
        'did': dataset_id
        }


except ValueError as e:
    if str(e) == "n_estimators must be an integer, got <class 'str'>.":
        flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
        dataset = openml.datasets.get_dataset(dataset_id)
        le = preprocessing.LabelEncoder()
        model = flow.model

        X, y, categorical_indicator, attribute_names = dataset.get_data(
            dataset_format='dataframe',
            target=target
        )

        X[target] = y
        X = X.dropna()
        attribute_names.append(target)

        for i, label in enumerate(attribute_names):
            if X.dtypes[i] not in ['float64', 'int']:
                X[label] = le.fit_transform(X[label])

        y = X[target]
        X = X.drop([target], axis=1)


        X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33, random_state=42)

        model.set_params(estimator__n_estimators=10)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        score = accuracy_score(y_test, preds)
        preds_labels = le.inverse_transform(preds)
        p = model.predict(predict)

        result = {
            'flow': flow_id,
            'target': target,
            'score': score,
            'did': dataset_id
            }

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
        preds_labels = le.inverse_transform(preds)
        p = model.predict(predict)
        print(p)
        result = {
            'flow': flow_id,
            'target': target,
            'score': score,
            'did': dataset_id
            }

except Exception as e:
    print(e)       
# except ModuleNotFoundError as e:
#     print(e)
#     result = {
#         'flow': flow_id,
#         'target': target,
#         'score': math.inf,
#         'did': dataset_id
#     }


# except ValueError as e:
#     print(e)
#     flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
#     dataset = openml.datasets.get_dataset(dataset_id)

#     model = flow.model

#     X, y, categorical_indicator, attribute_names = dataset.get_data(
#         dataset_format='dataframe',
#         target=target
#     )

#     X[target] = y
#     X = X.dropna()

#     le = preprocessing.LabelEncoder()
#     labels = X.columns.values.tolist()

#     for i, label in enumerate(labels):
#         if X.dtypes[i] == 'object':
#             X[label] = le.fit_transform(X[label])


#     y = X[target]
#     X = X.drop([target], axis=1)

#     model.fit(X, y)
#     preds = model.predict(X)

#     score = mean_squared_error(y, preds)

#     result = {
#         'flow': flow_id,
#         'target': target,
#         'score': score,
#         'did': dataset_id
#         }



# except TypeError as e:
#     flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
#     dataset = openml.datasets.get_dataset(dataset_id)

#     model = flow.model

#     X, y, categorical_indicator, attribute_names = dataset.get_data(
#         dataset_format='dataframe',
#         target=target
#     )

#     X[target] = y
#     X = X.dropna()

#     le = preprocessing.LabelEncoder()
#     labels = X.columns.values.tolist()

#     for i, label in enumerate(labels):
#         if X.dtypes[i] == 'object':
#             X[label] = le.fit_transform(X[label])


#     y = X[target]
#     X = X.drop([target], axis=1)

#     model.fit(X, y)
#     preds = model.predict(X)

#     score = mean_squared_error(y, preds)

#     result = {
#         'flow': flow_id,
#         'target': target,
#         'score': score,
#         'did': dataset_id
#         }

# except Exception as e:
#     print(e)
#     result = {
#         'flow': flow_id,
#         'target': target,
#         'score': "ERROR",
#         'did': dataset_id
#         }



# print(json.dumps(result))

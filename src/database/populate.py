import openml
import numpy as np 
from app.neo4j.openml_model import Dataset, Task, Flow, Run, graph
from itertools import combinations
import math

print(graph)

def compare_dataset(d1, d2):
    d_1 = openml.datasets.get_dataset(d1)
    d_2 = openml.datasets.get_dataset(d2)
    mf_1 = d_1.qualities
    mf_2 = d_2.qualities
    norm = []
    mf = list(set(mf_1).intersection(mf_2))

    for f in mf:
        if not math.isnan(mf_1[f]) and not math.isnan(mf_2[f]):
            norm.append(mf_1[f] - mf_2[f])
    
    norm = np.array(norm, dtype='float64')
    return np.linalg.norm(norm)

def get_datasets(limit):
    datasets = openml.datasets.list_datasets(size=limit)
    return [dataset[1] for dataset in  list(datasets.items())]

def get_pairs(datasets):
    pairs = combinations(datasets, 2)
    return list(pairs)

def get_tasks(did):
    tasks = openml.tasks.list_tasks(data_id=did)
    return [task[1] for task in list(tasks.items())]

def get_flows(offset):
    flows = openml.flows.list_flows(offset=offset)
    return [flow[1] for flow in list(flows.items())]


def get_runs(tid):
    runs = openml.runs.list_runs(task=[tid])
    return runs

def populate(limit):

    datasets = get_datasets(limit)
    pairs = get_pairs(datasets)

    for pair in pairs:
        d1 = pair[0]
        d2 = pair[1]


        if Dataset(did=d1['did']).fetch() != None \
            and Dataset(did=d2['did']).fetch() != None:

            print(f"Datasets {d1['name']} and {d2['name']} already in database.")
            continue
        else:
            distance = compare_dataset(d1, d2)

            print(f"Distance between {d1['name']} and {d2['name']} is {distance}.")

            dataset_1 = Dataset(did=d1['did'],
                                name=d1['name'],
                                file_format=d1['format'])
            dataset_2 = Dataset(did=d2['did'],
                                name=d2['name'],
                                file_format=d2['format'])
            dataset_1.save()
            dataset_2.save()
            dataset_1.add_connections(dataset_2, distance)

def populate_datasets(limit):


    datasets = get_datasets(limit)

    for dataset in datasets:
        datasets = get_datasets(limit)
        current = list(Dataset().all)
        dataset_obj = Dataset(did=dataset['did']).fetch()
        if dataset_obj in current:
            connections = dataset_obj.get_connections()
            others = current[:]
            others.remove(dataset_obj)
            unconnected = list(set(others) - set(connections))
            if len(unconnected) > 1:
                for to_connect in unconnected:
                    print(f"Connecting {to_connect} to {dataset_obj}.")
                    distance = compare_dataset(dataset['did'], to_connect.did)
                    dataset_obj.add_connections(to_connect, distance)
                    dataset_obj.save()
            else:
                print(f"Dataset {dataset_obj} is fully connected.")
        else:
            new = Dataset(
                did=dataset['did'],
                name=dataset['name'],
                file_format=dataset['format'],
            )
            print(f"Created new {new}.")
            new.save()
            for to_connect in current:
                    print(f"Connecting {to_connect} to {new}.")
                    distance = compare_dataset(dataset['did'], to_connect.did)
                    new.add_connections(new, distance)
                    new.save() 


def populate_tasks():

    datasets = list(Dataset().all)
    
    for dataset in datasets:
        current = dataset.get_tasks()
        print(f"On dataset {dataset}")
        new = get_tasks(dataset.did)
        for new_task in new:
            task_obj = Task(tid=new_task['tid']).fetch()
            if task_obj not in current:
                task_obj = Task(
                    tid=new_task['tid'],
                    task_type=new_task['task_type'],
                    task_type_id=new_task['ttid'],
                )
                for key, value in new_task.items():
                    if hasattr(task_obj, key):
                        setattr(task_obj, key, value)
                task_obj.save()
                print(f"Adding new task {task_obj}")
                dataset.add_task(task_obj)

# def populate_flows(offset):
#     flows = get_tasks(offset)
#     for flow in flows:
#         f = flows.get_flow(flow['flow_id'])
#         ti =
#     pass


populate_datasets(50)


    
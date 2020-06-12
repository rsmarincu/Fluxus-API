import openml
import numpy as np 
from app.neo4j.openml_model import Dataset
from itertools import combinations
import math
import pprint

pp = pprint.PrettyPrinter(indent=4)

def compare_dataset(d1, d2):
    d_1 = openml.datasets.get_dataset(d1['did'])
    d_2 = openml.datasets.get_dataset(d2['did'])
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

def populate(limit):

    datasets = get_datasets(limit)
    pairs = get_pairs(datasets)

    for pair in pairs:
        d1 = pair[0]
        d2 = pair[1]

        print(f"Adding database {d1['name']}.")
        print(f"Adding database {d2['name']}.")

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


populate(50)
    
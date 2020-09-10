import json
import filecmp

test_file = "tests/test.csv"
expected_labels = ["age","sex","chest","resting_blood_pressure","serum_cholestoral","fasting_blood_sugar","resting_electrocardiographic_results","maximum_heart_rate_achieved","exercise_induced_angina","oldpeak","slope","number_of_major_vessels","thal","class"]

def test_pandas_hello(app, client):
    res = client.get('/hello/')
    assert res.status_code == 200
    expected = {"message":"Hello from the pandas endpoint!"}
    assert expected == json.loads(res.get_data(as_text=True))

def test_pandas_labels(app, client):
    file = open(test_file, 'rb')
    case_labels = {
        'file':file
    }
    res = client.post('/labels/',
        data=case_labels
    )
    assert res.status_code == 200
    assert expected_labels == json.loads(res.get_data(as_text=True))

def test_pandas_columns(app, client):
    file = open(test_file, 'rb')
    case_columns = {
        'file':file,
        'labels':["age", "sex"]
    }
    res = client.post('/columns/',
        data=case_columns
    )

    assert res.status_code == 200

    with open("tests/result_columns.csv", "wb") as f:
        f.write(res.get_data())
    
    assert filecmp.cmp('tests/result_columns.csv', 'tests/expected_columns.csv')

def test_pandas_countnan(app, client):
    file = open(test_file, 'rb')
    case_countnan = {
        'file':file,
    }
    res = client.post('/countnan/',
        data=case_countnan
    )

    assert res.status_code == 200
    assert 0 == json.loads(res.get_data(as_text=True))
   
def test_pandas_dropnan(app, client):
    file = open(test_file, 'rb')
    case_dropnan = {
        'file':file,
    }
    res = client.post('/dropnan/',
        data=case_dropnan
    )

    assert res.status_code == 200

    with open("tests/result_dropna.csv", "wb") as f:
        f.write(res.get_data())
    
    assert filecmp.cmp('tests/result_dropna.csv', 'tests/expected_dropna.csv')
   
def test_pandas_datasets(app, client):

    res = client.get('/datasets/')
    assert res.status_code == 200

    with open("tests/datasets.json") as f:
        datasets = json.load(f)
        assert datasets == json.loads(res.get_data(as_text=True))


def test_pandas_load(app, client):

    case_load = {
        'did':53,
    }

    res = client.get('/load/',
        data=case_load
    )

    assert res.status_code == 200

    with open("tests/result_load.csv", "wb") as f:
        f.write(res.get_data())
    
    assert filecmp.cmp('tests/result_load.csv', 'tests/expected_load.csv')
   
def test_pandas_getrow(app, client):
    file = open(test_file, 'rb')
    case_getrow = {
        'index': 1,
        'file': file
    }

    res = client.post('/row/',
        data=case_getrow
    )

    assert res.status_code == 200

    with open("tests/result_row.csv", "wb") as f:
        f.write(res.get_data())
    
    assert filecmp.cmp('tests/result_row.csv', 'tests/expected_row.csv')

def test_pandas_dropcolumns(app, client):
    file = open(test_file, 'rb')
    case_getrow = {
        'labels': 'age',
        'file': file
    }

    res = client.post('/dropcolumns/',
        data=case_getrow
    )

    assert res.status_code == 200

    with open("tests/result_dropcolumns.csv", "wb") as f:
        f.write(res.get_data())
    
    assert filecmp.cmp('tests/result_dropcolumns.csv', 'tests/expected_dropcolumns.csv')
   
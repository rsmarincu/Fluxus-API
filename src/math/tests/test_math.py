import json
import pytest
import filecmp

case_lists = {
        "as":[1, 2],
        "bs":[3, 4]
    }

case_single = {
        "as":[1, 2],
        "bs":[4]
    }

test_file = "tests/test.csv"



expected_lists_add = [4, 6]
expected_single_add = [5, 6]
expected_file_add = "tests/expected_add.csv"

expected_lists_divide = [0.3333333333333333, 0.5]
expected_single_divide = [0.25, 0.5]
expected_file_divide = "tests/expected_divide.csv"

expected_lists_multiply = [3, 8]
expected_single_multiply = [4, 8]
expected_file_multiply = "tests/expected_multiply.csv"

expected_lists_subtract = [-2, -2]
expected_single_subtract = [-3, -2]
expected_file_subtract = "tests/expected_subtract.csv"

def test_math_hello(app, client):
    res = client.get('/hello/')
    assert res.status_code == 200
    expected = {"message":"Hello from the math endpoint"}
    assert expected == json.loads(res.get_data(as_text=True))

def test_math_add(app, client):
    res = client.post('/add/', 
        data=case_lists
    )
    assert res.status_code == 200
    assert expected_lists_add == json.loads(res.get_data(as_text=True))

    res = client.post('/add/', 
        data=case_single
    )
    assert res.status_code == 200
    assert expected_single_add == json.loads(res.get_data(as_text=True))

    file = open(test_file, 'rb')
    case_file = {
        'file':file,
        'bs':1
    }
    res = client.post('/add/', 
        data=case_file
    )
    assert res.status_code == 200
    with open('tests/result_add.csv', 'wb') as f:
        f.write(res.get_data())
    assert filecmp.cmp(expected_file_add, 'tests/result_add.csv', shallow=False)
    file.close()

def test_math_divide(app, client):
    res = client.post('/divide/', 
        data=case_lists
    )
    assert res.status_code == 200
    assert expected_lists_divide == json.loads(res.get_data(as_text=True))

    res = client.post('/divide/', 
        data=case_single
    )
    assert res.status_code == 200
    assert expected_single_divide == json.loads(res.get_data(as_text=True))

    file = open(test_file, 'rb')
    case_file = {
        'file':file,
        'bs':1
    }
    res = client.post('/divide/', 
        data=case_file
    )

    assert res.status_code == 200
    with open('tests/result_divide.csv', 'wb') as f:
        f.write(res.get_data())
    assert filecmp.cmp(expected_file_divide, 'tests/result_divide.csv', shallow=False)
    file.close()

def test_math_multiply(app, client):
    res = client.post('/multiply/', 
        data=case_lists
    )
    assert res.status_code == 200
    assert expected_lists_multiply == json.loads(res.get_data(as_text=True))

    res = client.post('/multiply/', 
        data=case_single
    )
    assert res.status_code == 200
    assert expected_single_multiply == json.loads(res.get_data(as_text=True))

    file = open(test_file, 'rb')
    case_file = {
        'file':file,
        'bs':1
    }
    res = client.post('/multiply/', 
        data=case_file
    )

    assert res.status_code == 200
    with open('tests/result_multiply.csv', 'wb') as f:
        f.write(res.get_data())
    assert filecmp.cmp(expected_file_multiply, 'tests/result_multiply.csv', shallow=False)
    file.close()
    
def test_math_subtract(app, client):
    res = client.post('/subtract/', 
        data=case_lists
    )
    assert res.status_code == 200
    assert expected_lists_subtract == json.loads(res.get_data(as_text=True))

    res = client.post('/subtract/', 
        data=case_single
    )
    assert res.status_code == 200
    assert expected_single_subtract == json.loads(res.get_data(as_text=True))

    file = open(test_file, 'rb')
    case_file = {
        'file':file,
        'bs':1
    }
    res = client.post('/subtract/', 
        data=case_file
    )

    assert res.status_code == 200
    with open('tests/result_subtract.csv', 'wb') as f:
        f.write(res.get_data())
    assert filecmp.cmp(expected_file_subtract, 'tests/result_subtract.csv', shallow=False)
    file.close()
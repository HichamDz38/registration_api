from fastapi.testclient import TestClient
import datetime
from app.main import app

client = TestClient(app)


def test_user_validation():
    response = client.get("/users/validation/?key=7815",
                          auth=("john", "secret"))
    assert response.status_code == 401


def test_add_employee():
    response = client.post("/employee",
                           json={"emp_id": 33,
                                 "first_name": "hicham2",
                                 "last_name": "dachir2",
                                 "gender": 'M',
                                 "birth_date": "1992-01-01",
                                 "hire_date": "2022-01-03"})
    assert response.status_code == 201
    assert response.json() == {"message": "employee created 33"}


def test_get_employee1():
    response = client.get("/employee/33")
    assert response.status_code == 200
    assert response.json() == {"emp_id": 33,
                               "first_name": "hicham2",
                               "last_name": "dachir2",
                               "gender": 'M',
                               "birth_date": "1992-01-01",
                               "hire_date": "2022-01-03"}


def test_update_employee():
    response = client.patch("/employee/33",
                            json={"emp_id": 33,
                                  "first_name": "hicham212",
                                  "last_name": "dachir212",
                                  "birth_date": "1992-01-01",
                                  "gender": "F",
                                  "hire_date": "2022-01-03"})
    assert response.status_code == 200
    assert response.json() == {"emp_id": 33,
                               "first_name": "hicham212",
                               "last_name": "dachir212",
                               "gender": "F",
                               "birth_date": "1992-01-01",
                               "hire_date": "2022-01-03"}


def test_get_employee2():
    response = client.get("/employee/33")
    assert response.status_code == 200
    assert response.json() == {"emp_id": 33,
                               "first_name": "hicham212",
                               "last_name": "dachir212",
                               "gender": "F",
                               "birth_date": "1992-01-01",
                               "hire_date": "2022-01-03"}


def test_delete_employee():
    response = client.delete("/employee/33")
    assert response.status_code == 200


def test_get_invalid_employee():
    response = client.get("/employee/33")
    assert response.status_code == 404

from fastapi.testclient import TestClient
from sql_app.main import app

client = TestClient(app)

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InN1c29uZyIsImVtYWlsIjoic3Vzb25nQHN0dWRlbnQuNDJzZW91bC5rciJ9.MW1_KxAgPAgJTOVEwwf4VghLS_ucbGXFzC91tdR-N8k"  # 실제 사용할 토큰
headers = {"Authorization": f"Bearer {token}"}


def test_borrow():
	response = client.post("/umbrellas/borrow?umbrella_id=4", headers=headers)
	assert response.status_code == 200
	assert response.json()["user_name"] == "susong"
	assert response.json()["umbrella_id"] == 4

def test_return():
	response = client.post("/umbrellas/return?umbrella_id=4", headers=headers)
	assert response.status_code == 200
	assert response.json()["user_name"] == "susong"
	assert response.json()["umbrella_id"] == 4

def test_borrow_twice():
	response = client.post("/umbrellas/borrow?umbrella_id=4", headers=headers)
	assert response.status_code == 200
	response = client.post("/umbrellas/borrow?umbrella_id=4", headers=headers)
	assert response.status_code == 400

def test_return_twice():
	response = client.post("/umbrellas/return?umbrella_id=4", headers=headers)
	assert response.status_code == 200
	response = client.post("/umbrellas/return?umbrella_id=4", headers=headers)
	assert response.status_code == 400

def test_borrow_no_token():
	response = client.post("/umbrellas/borrow?umbrella_id=4")
	assert response.status_code == 401

def test_return_no_token():
	response = client.post("/umbrellas/return?umbrella_id=4")
	assert response.status_code == 401
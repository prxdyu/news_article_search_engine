import pytest
from app import app # importing the app from app.py
import re



# creating a resuable client  for testing using pytest fixture
@pytest.fixture
def client():
    return app.test_client()


def test_ping(client):
    # sending a GET request to ping endpoint using the client
    response = client.get('/ping')
    # asserting the status of the request
    assert response.status_code == 200
    # parsing the JSON response
    response_json = response.get_json()
    # asserting the content of the request
    assert response_json["status"] == "OK"
    assert "timestamp" in response_json


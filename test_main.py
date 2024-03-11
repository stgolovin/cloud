import pytest
from main import app, get_extension_list

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200


def test_extlist_route(client):
    response = client.get('/extlist/')
    assert response.status_code == 401


def test_randomext_route(client):
    response = client.get('/randomext/')
    assert response.status_code == 200

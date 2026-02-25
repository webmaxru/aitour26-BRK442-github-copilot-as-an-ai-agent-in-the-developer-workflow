import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_and_get_product(client):
    # Create
    rv = client.post('/products', json={'name': 'Test', 'description': 'Desc'})
    assert rv.status_code == 201
    product = rv.get_json()
    # Get
    rv = client.get(f"/products/{product['id']}")
    assert rv.status_code == 200
    assert rv.get_json()['name'] == 'Test'

def test_update_product(client):
    rv = client.post('/products', json={'name': 'Test', 'description': 'Desc'})
    product = rv.get_json()
    rv = client.put(f"/products/{product['id']}", json={'name': 'Updated', 'description': 'NewDesc'})
    assert rv.status_code == 200
    assert rv.get_json()['name'] == 'Updated'

def test_delete_product(client):
    rv = client.post('/products', json={'name': 'Test', 'description': 'Desc'})
    product = rv.get_json()
    rv = client.delete(f"/products/{product['id']}")
    assert rv.status_code == 204
    rv = client.get(f"/products/{product['id']}")
    assert rv.status_code == 404

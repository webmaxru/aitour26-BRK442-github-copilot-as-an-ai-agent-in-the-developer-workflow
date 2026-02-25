# Unit test file
import json
import pytest
from app import app, data


@pytest.fixture(autouse=True)
def clear_data():
    data.clear()
    yield
    data.clear()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_index_returns_html(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'Product Store' in res.data


def test_get_products_empty(client):
    res = client.get('/products')
    assert res.status_code == 200
    assert json.loads(res.data) == []


def test_create_product(client):
    res = client.post('/products', json={'name': 'Test Product', 'description': 'A test', 'category': 'Hardware'})
    assert res.status_code == 201
    body = json.loads(res.data)
    assert body['name'] == 'Test Product'
    assert body['description'] == 'A test'
    assert body['category'] == 'Hardware'
    assert 'id' in body


def test_create_product_missing_name(client):
    res = client.post('/products', json={'description': 'No name'})
    assert res.status_code == 400


def test_get_product(client):
    created = json.loads(client.post('/products', json={'name': 'Item'}).data)
    res = client.get(f"/products/{created['id']}")
    assert res.status_code == 200
    assert json.loads(res.data)['name'] == 'Item'


def test_get_product_not_found(client):
    res = client.get('/products/nonexistent')
    assert res.status_code == 404


def test_update_product(client):
    created = json.loads(client.post('/products', json={'name': 'Old'}).data)
    res = client.put(f"/products/{created['id']}", json={'name': 'New', 'description': 'Updated', 'category': 'Plumbing'})
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body['name'] == 'New'
    assert body['category'] == 'Plumbing'


def test_update_product_not_found(client):
    res = client.put('/products/nonexistent', json={'name': 'X'})
    assert res.status_code == 404


def test_delete_product(client):
    created = json.loads(client.post('/products', json={'name': 'ToDelete'}).data)
    res = client.delete(f"/products/{created['id']}")
    assert res.status_code == 204
    assert client.get(f"/products/{created['id']}").status_code == 404


def test_delete_product_not_found(client):
    res = client.delete('/products/nonexistent')
    assert res.status_code == 404
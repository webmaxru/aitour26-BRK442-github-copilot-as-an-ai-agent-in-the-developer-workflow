import pytest
import json
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
    assert res.get_json() == []


def test_create_product(client):
    res = client.post('/products', json={'name': 'Widget', 'description': 'A widget'})
    assert res.status_code == 201
    body = res.get_json()
    assert body['name'] == 'Widget'
    assert body['description'] == 'A widget'
    assert 'id' in body


def test_create_product_missing_name(client):
    res = client.post('/products', json={'description': 'No name'})
    assert res.status_code == 400


def test_create_product_no_body(client):
    res = client.post('/products', content_type='application/json', data='')
    assert res.status_code == 400


def test_get_product(client):
    create_res = client.post('/products', json={'name': 'Widget'})
    product_id = create_res.get_json()['id']
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 200
    assert res.get_json()['name'] == 'Widget'


def test_get_product_not_found(client):
    res = client.get('/products/nonexistent-id')
    assert res.status_code == 404


def test_update_product(client):
    create_res = client.post('/products', json={'name': 'Old Name'})
    product_id = create_res.get_json()['id']
    res = client.put(f'/products/{product_id}', json={'name': 'New Name', 'description': 'Updated'})
    assert res.status_code == 200
    body = res.get_json()
    assert body['name'] == 'New Name'
    assert body['description'] == 'Updated'


def test_update_product_not_found(client):
    res = client.put('/products/nonexistent-id', json={'name': 'X'})
    assert res.status_code == 404


def test_update_product_missing_name(client):
    create_res = client.post('/products', json={'name': 'Widget'})
    product_id = create_res.get_json()['id']
    res = client.put(f'/products/{product_id}', json={'description': 'No name'})
    assert res.status_code == 400


def test_delete_product(client):
    create_res = client.post('/products', json={'name': 'Widget'})
    product_id = create_res.get_json()['id']
    res = client.delete(f'/products/{product_id}')
    assert res.status_code == 204
    assert client.get(f'/products/{product_id}').status_code == 404


def test_delete_product_not_found(client):
    res = client.delete('/products/nonexistent-id')
    assert res.status_code == 404


def test_get_all_products_after_create(client):
    client.post('/products', json={'name': 'A'})
    client.post('/products', json={'name': 'B'})
    res = client.get('/products')
    assert res.status_code == 200
    assert len(res.get_json()) == 2
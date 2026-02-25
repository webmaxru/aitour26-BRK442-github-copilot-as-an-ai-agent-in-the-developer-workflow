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
    with app.test_client() as client:
        yield client


def test_get_products_empty(client):
    response = client.get('/products')
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_product(client):
    response = client.post('/products', json={'name': 'Widget', 'description': 'A widget'})
    assert response.status_code == 201
    body = response.get_json()
    assert body['name'] == 'Widget'
    assert body['description'] == 'A widget'
    assert 'id' in body


def test_create_product_missing_name(client):
    response = client.post('/products', json={'description': 'No name'})
    assert response.status_code == 400


def test_create_product_no_body(client):
    response = client.post('/products', content_type='application/json', data='')
    assert response.status_code == 400


def test_get_products_returns_created(client):
    client.post('/products', json={'name': 'Widget'})
    response = client.get('/products')
    assert response.status_code == 200
    products = response.get_json()
    assert len(products) == 1
    assert products[0]['name'] == 'Widget'


def test_get_product_by_id(client):
    created = client.post('/products', json={'name': 'Gadget'}).get_json()
    product_id = created['id']
    response = client.get(f'/products/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Gadget'


def test_get_product_not_found(client):
    response = client.get('/products/nonexistent-id')
    assert response.status_code == 404


def test_update_product(client):
    created = client.post('/products', json={'name': 'Old Name'}).get_json()
    product_id = created['id']
    response = client.put(f'/products/{product_id}', json={'name': 'New Name', 'description': 'Updated'})
    assert response.status_code == 200
    body = response.get_json()
    assert body['name'] == 'New Name'
    assert body['description'] == 'Updated'


def test_update_product_not_found(client):
    response = client.put('/products/nonexistent-id', json={'name': 'X'})
    assert response.status_code == 404


def test_update_product_missing_name(client):
    created = client.post('/products', json={'name': 'Widget'}).get_json()
    product_id = created['id']
    response = client.put(f'/products/{product_id}', json={'description': 'Only description'})
    assert response.status_code == 400


def test_delete_product(client):
    created = client.post('/products', json={'name': 'ToDelete'}).get_json()
    product_id = created['id']
    response = client.delete(f'/products/{product_id}')
    assert response.status_code == 204
    get_response = client.get(f'/products/{product_id}')
    assert get_response.status_code == 404


def test_delete_product_not_found(client):
    response = client.delete('/products/nonexistent-id')
    assert response.status_code == 404


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Product Store' in response.data
# Unit test file
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


# --- UI route ---

def test_index_returns_html(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Product Store' in response.data
    assert b'text/html' in response.content_type.encode()


# --- GET /products ---

def test_get_products_empty(client):
    response = client.get('/products')
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_products_returns_list(client):
    client.post('/products', json={'name': 'Widget', 'description': 'A widget'})
    response = client.get('/products')
    assert response.status_code == 200
    products = response.get_json()
    assert len(products) == 1
    assert products[0]['name'] == 'Widget'


# --- GET /products/<id> ---

def test_get_product_by_id(client):
    post = client.post('/products', json={'name': 'Gadget'})
    product_id = post.get_json()['id']
    response = client.get(f'/products/{product_id}')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Gadget'


def test_get_product_not_found(client):
    response = client.get('/products/nonexistent-id')
    assert response.status_code == 404


# --- POST /products ---

def test_create_product(client):
    response = client.post('/products', json={'name': 'Doohickey', 'description': 'A doohickey'})
    assert response.status_code == 201
    product = response.get_json()
    assert product['name'] == 'Doohickey'
    assert product['description'] == 'A doohickey'
    assert 'id' in product


def test_create_product_missing_name(client):
    response = client.post('/products', json={'description': 'No name'})
    assert response.status_code == 400


def test_create_product_no_body(client):
    response = client.post('/products', content_type='application/json', data='')
    assert response.status_code == 400


def test_create_product_default_description(client):
    response = client.post('/products', json={'name': 'Plain'})
    assert response.status_code == 201
    assert response.get_json()['description'] == ''


# --- PUT /products/<id> ---

def test_update_product(client):
    post = client.post('/products', json={'name': 'Old Name'})
    product_id = post.get_json()['id']
    response = client.put(f'/products/{product_id}', json={'name': 'New Name', 'description': 'Updated'})
    assert response.status_code == 200
    updated = response.get_json()
    assert updated['name'] == 'New Name'
    assert updated['description'] == 'Updated'


def test_update_product_not_found(client):
    response = client.put('/products/nonexistent-id', json={'name': 'X'})
    assert response.status_code == 404


def test_update_product_missing_name(client):
    post = client.post('/products', json={'name': 'Existing'})
    product_id = post.get_json()['id']
    response = client.put(f'/products/{product_id}', json={'description': 'No name'})
    assert response.status_code == 400


# --- DELETE /products/<id> ---

def test_delete_product(client):
    post = client.post('/products', json={'name': 'Temp'})
    product_id = post.get_json()['id']
    response = client.delete(f'/products/{product_id}')
    assert response.status_code == 204
    assert client.get(f'/products/{product_id}').status_code == 404


def test_delete_product_not_found(client):
    response = client.delete('/products/nonexistent-id')
    assert response.status_code == 404

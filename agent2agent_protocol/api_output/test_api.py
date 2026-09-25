import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"

@pytest.fixture
def created_todo():
    """Fixture to create a todo item for tests that require an existing resource."""
    payload = {
        "title": "Test Todo",
        "description": "Integration test description"
    }
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    todo = response.json()
    yield todo
    # Cleanup after test
    requests.delete(f"{BASE_URL}/todos/{todo.get('id')}")


def test_create_todo_success():
    """Test POST /todos - Happy Path: Create a new todo successfully."""
    payload = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread, and vegetables"
    }
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data and isinstance(data["id"], str)
    assert "title" in data and isinstance(data["title"], str)
    assert "description" in data and isinstance(data["description"], str)
    assert "completed" in data and isinstance(data["completed"], bool)
    assert "created_at" in data and isinstance(data["created_at"], str)

    # Cleanup created todo
    requests.delete(f"{BASE_URL}/todos/{data['id']}")


def test_create_todo_bad_request():
    """Test POST /todos - Error Case: Invalid input (missing required title) returns 400."""
    payload = {
        "description": "Missing title field"
    }
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 400
    
    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], str)


def test_list_todos_success():
    """Test GET /todos - Happy Path: List all todos successfully."""
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data and isinstance(data["data"], list)
    assert "count" in data and isinstance(data["count"], int)


def test_get_todo_by_id_success(created_todo):
    """Test GET /todos/{id} - Happy Path: Retrieve an existing todo by ID."""
    todo_id = created_todo["id"]
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == todo_id
    assert "title" in data and isinstance(data["title"], str)
    assert "completed" in data and isinstance(data["completed"], bool)


def test_get_todo_by_id_not_found():
    """Test GET /todos/{id} - Error Case: Retrieve non-existent todo returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}/todos/{non_existent_id}")
    assert response.status_code == 404
    
    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], str)


def test_update_todo_success(created_todo):
    """Test PUT /todos/{id} - Happy Path: Update an existing todo successfully."""
    todo_id = created_todo["id"]
    payload = {
        "title": "Buy groceries updated",
        "description": "Added more items",
        "completed": True
    }
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert data["id"] == todo_id
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] == payload["completed"]
    assert "updated_at" in data and isinstance(data["updated_at"], str)


def test_update_todo_bad_request(created_todo):
    """Test PUT /todos/{id} - Error Case: Invalid input type returns 400."""
    todo_id = created_todo["id"]
    payload = {
        "completed": "not-a-boolean"
    }
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    assert response.status_code == 400
    
    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], str)


def test_update_todo_not_found():
    """Test PUT /todos/{id} - Error Case: Update non-existent todo returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "title": "Should fail"
    }
    response = requests.put(f"{BASE_URL}/todos/{non_existent_id}", json=payload)
    assert response.status_code == 404
    
    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], str)


def test_delete_todo_success(created_todo):
    """Test DELETE /todos/{id} - Happy Path: Delete an existing todo successfully."""
    todo_id = created_todo["id"]
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 204
    assert response.text == ""


def test_delete_todo_not_found():
    """Test DELETE /todos/{id} - Error Case: Delete non-existent todo returns 404."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = requests.delete(f"{BASE_URL}/todos/{non_existent_id}")
    assert response.status_code == 404
    
    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data and isinstance(data["error"], str)
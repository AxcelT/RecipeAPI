import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from app import models, schemas, crud

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    # Drop all tables and recreate them before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def create_test_user(client):
    # Ensure the test user exists before running tests
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"},
    )
    if response.status_code not in {200, 400}:
        pytest.fail(f"Failed to create test user: {response.status_code} {response.json()}")

def test_create_user(client):
    response = client.post(
        "/users/",
        json={"username": "testuser2", "email": "test2@example.com", "password": "testpassword"},
    )
    if response.status_code == 400:
        assert response.json()["detail"] == "Username already registered"
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser2"
        assert "id" in data

def get_access_token(client):
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.status_code} {login_response.json()}"
    return login_response.json()["access_token"]

def test_create_recipe(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": "Test Recipe", "ingredients": "Test Ingredient", "steps": "Test Step", "prep_time": 10},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Recipe"
    assert "id" in data

def test_read_recipes(client):
    response = client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_recipes_with_pagination(client):
    response = client.get("/recipes/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2

def test_search_recipes(client):
    response = client.get("/recipes/search/?query=Test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_suggest_recipes(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/recipes/suggestions/",
        headers=headers,
        params=[("ingredients", "Test Ingredient")]
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_unauthorized_access(client):
    response = client.post(
        "/recipes/",
        json={"name": "Unauthorized Recipe", "ingredients": "None", "steps": "None", "prep_time": 0},
    )
    assert response.status_code == 401

def test_read_recipes_empty_db(client):
    response = client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_recipe_with_missing_fields(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": "Incomplete Recipe"},
        headers=headers,
    )
    assert response.status_code == 422

def test_create_recipe_with_invalid_data(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": 123, "ingredients": [], "steps": {}, "prep_time": "ten"},
        headers=headers,
    )
    assert response.status_code == 422

def test_rate_recipe(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": "Rate Test Recipe", "ingredients": "Test Ingredient", "steps": "Test Step", "prep_time": 10},
        headers=headers,
    )
    recipe_id = response.json()["id"]
    response = client.post(
        f"/recipes/{recipe_id}/ratings/",
        json={"rating": 5},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5

def test_comment_recipe(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": "Comment Test Recipe", "ingredients": "Test Ingredient", "steps": "Test Step", "prep_time": 10},
        headers=headers,
    )
    recipe_id = response.json()["id"]
    response = client.post(
        f"/recipes/{recipe_id}/comments/",
        json={"text": "Great recipe!"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Great recipe!"

def test_read_comments(client, create_test_user):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/recipes/",
        json={"name": "Read Comment Test Recipe", "ingredients": "Test Ingredient", "steps": "Test Step", "prep_time": 10},
        headers=headers,
    )
    recipe_id = response.json()["id"]
    client.post(
        f"/recipes/{recipe_id}/comments/",
        json={"text": "First comment"},
        headers=headers,
    )
    client.post(
        f"/recipes/{recipe_id}/comments/",
        json={"text": "Second comment"},
        headers=headers,
    )
    response = client.get(
        f"/recipes/{recipe_id}/comments/",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["text"] == "First comment"
    assert data[1]["text"] == "Second comment"

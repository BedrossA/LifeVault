"""Tests for authentication endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

#client = TestClient(app)

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test@1234",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user(client):
    """Test registering duplicate user fails"""
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "duplicateuser",
            "password": "Test@1234"
        }
    )
    
    # Duplicate registration should fail
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "duplicateuser",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 400

def test_login_success(client):
    """Test successful login"""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "Test@1234"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401

def test_get_current_user(client):
    """Test getting current user info"""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "Test@1234"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "currentuser",
            "password": "Test@1234"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
   	"/api/v1/auth/me",
    	headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"

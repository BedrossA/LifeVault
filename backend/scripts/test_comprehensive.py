"""Comprehensive test suite for LifeVault features"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration with strong password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_weak_password(self, client):
        """Test that weak passwords are rejected"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "weak"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_register_duplicate_username(self, client):
        """Test duplicate username rejection"""
        user_data = {
            "email": "dup1@example.com",
            "username": "duplicateuser",
            "password": "SecureP@ssw0rd123"
        }
        
        # First registration
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Duplicate registration
        user_data["email"] = "dup2@example.com"  # Different email, same username
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
    
    def test_login_oauth2_format(self, client):
        """Test login with OAuth2 format"""
        # Register user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "oauth@example.com",
                "username": "oauthuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        # Login with OAuth2 format (form data)
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "oauthuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_wrong_credentials(self, client):
        """Test login with wrong credentials"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client):
        """Test getting current authenticated user"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "current@example.com",
                "username": "currentuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "currentuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"
    
    def test_refresh_token(self, client):
        """Test token refresh"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "username": "refreshuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "refreshuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        refresh_token = login_resp.json()["refresh_token"]
        
        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_logout(self, client):
        """Test logout"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout@example.com",
                "username": "logoutuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "logoutuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestAnalytics:
    """Test analytics endpoints"""
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client"""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "analytics@example.com",
                "username": "analyticsuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "analyticsuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        return client
    
    def test_create_entry(self, authenticated_client):
        """Test creating analytics entry"""
        response = authenticated_client.post(
            "/api/v1/analytics/entries",
            json={
                "category": "health",
                "metric": "steps",
                "value": 10000,
                "unit": "steps",
                "notes": "Daily walk"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["category"] == "health"
        assert data["metric"] == "steps"
        assert data["value"] == 10000
        assert "id" in data
    
    def test_create_entry_validation(self, authenticated_client):
        """Test entry validation"""
        # Missing required fields
        response = authenticated_client.post(
            "/api/v1/analytics/entries",
            json={
                "category": "health"
                # Missing metric and value
            }
        )
        assert response.status_code == 422
    
    def test_list_entries(self, authenticated_client):
        """Test listing entries"""
        # Create multiple entries
        for i in range(5):
            authenticated_client.post(
                "/api/v1/analytics/entries",
                json={
                    "category": "fitness",
                    "metric": "calories",
                    "value": 400 + i * 50
                }
            )
        
        # List all entries
        response = authenticated_client.get("/api/v1/analytics/entries")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5
    
    def test_filter_entries_by_category(self, authenticated_client):
        """Test filtering entries by category"""
        # Create entries in different categories
        authenticated_client.post(
            "/api/v1/analytics/entries",
            json={"category": "health", "metric": "steps", "value": 8000}
        )
        authenticated_client.post(
            "/api/v1/analytics/entries",
            json={"category": "fitness", "metric": "calories", "value": 500}
        )
        
        # Filter by category
        response = authenticated_client.get(
            "/api/v1/analytics/entries?category=health"
        )
        assert response.status_code == 200
        data = response.json()
        assert all(entry["category"] == "health" for entry in data)
    
    def test_get_statistics(self, authenticated_client):
        """Test getting analytics statistics"""
        # Create some entries
        for i in range(3):
            authenticated_client.post(
                "/api/v1/analytics/entries",
                json={
                    "category": "productivity",
                    "metric": "hours",
                    "value": 8 + i
                }
            )
        
        # Get stats
        response = authenticated_client.get("/api/v1/analytics/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "categories" in data
        assert data["total_entries"] >= 3
    
    def test_update_entry(self, authenticated_client):
        """Test updating an entry"""
        # Create entry
        create_resp = authenticated_client.post(
            "/api/v1/analytics/entries",
            json={
                "category": "health",
                "metric": "weight",
                "value": 70.0,
                "unit": "kg"
            }
        )
        entry_id = create_resp.json()["id"]
        
        # Update entry
        response = authenticated_client.put(
            f"/api/v1/analytics/entries/{entry_id}",
            json={
                "category": "health",
                "metric": "weight",
                "value": 69.5,
                "unit": "kg",
                "notes": "Lost some weight!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == 69.5
        assert data["notes"] == "Lost some weight!"
    
    def test_delete_entry(self, authenticated_client):
        """Test deleting an entry"""
        # Create entry
        create_resp = authenticated_client.post(
            "/api/v1/analytics/entries",
            json={
                "category": "test",
                "metric": "test_metric",
                "value": 100
            }
        )
        entry_id = create_resp.json()["id"]
        
        # Delete entry
        response = authenticated_client.delete(
            f"/api/v1/analytics/entries/{entry_id}"
        )
        assert response.status_code == 204
        
        # Verify deletion
        get_resp = authenticated_client.get(
            f"/api/v1/analytics/entries/{entry_id}"
        )
        assert get_resp.status_code == 404


class TestGoals:
    """Test goals endpoints"""
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client"""
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "goals@example.com",
                "username": "goalsuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "goalsuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        return client
    
    def test_create_goal(self, authenticated_client):
        """Test creating a goal"""
        response = authenticated_client.post(
            "/api/v1/analytics/goals",
            json={
                "metric": "steps",
                "category": "health",
                "target_value": 10000,
                "unit": "steps"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["metric"] == "steps"
        assert data["target_value"] == 10000
        assert "id" in data
    
    def test_list_goals(self, authenticated_client):
        """Test listing goals"""
        # Create goals
        for metric, target in [("steps", 10000), ("calories", 2000)]:
            authenticated_client.post(
                "/api/v1/analytics/goals",
                json={
                    "metric": metric,
                    "category": "health",
                    "target_value": target
                }
            )
        
        # List goals
        response = authenticated_client.get("/api/v1/analytics/goals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


class TestIntelligence:
    """Test intelligence/analytics features"""
    
    @pytest.fixture
    def authenticated_client_with_data(self, client):
        """Create authenticated client with sample data"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "intel@example.com",
                "username": "inteluser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "inteluser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        
        # Create sample data
        for i in range(10):
            client.post(
                "/api/v1/analytics/entries",
                json={
                    "category": "health",
                    "metric": "sleep_hours",
                    "value": 7 + (i % 3)
                }
            )
            client.post(
                "/api/v1/analytics/entries",
                json={
                    "category": "fitness",
                    "metric": "exercise_minutes",
                    "value": 30 + i * 5
                }
            )
        
        return client
    
    def test_get_correlations(self, authenticated_client_with_data):
        """Test correlation detection"""
        response = authenticated_client_with_data.get(
            "/api/v1/intelligence/correlations?metrics=sleep_hours,exercise_minutes"
        )
        assert response.status_code == 200
        # May or may not find correlations depending on data
    
    def test_detect_anomalies(self, authenticated_client_with_data):
        """Test anomaly detection"""
        response = authenticated_client_with_data.get(
            "/api/v1/intelligence/anomalies/sleep_hours?method=zscore"
        )
        assert response.status_code == 200
    
    def test_get_forecast(self, authenticated_client_with_data):
        """Test predictive forecasting"""
        response = authenticated_client_with_data.get(
            "/api/v1/intelligence/forecast/sleep_hours?periods=7&method=linear"
        )
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) == 7


class TestSecurity:
    """Test security features"""
    
    def test_unauthorized_access(self, client):
        """Test that unauthorized requests are rejected"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """Test that invalid tokens are rejected"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "admin' OR '1'='1",
                "password": "password"
            }
        )
        assert response.status_code == 401  # Should fail authentication


class TestPerformance:
    """Test performance aspects"""
    
    def test_bulk_entry_creation(self, client):
        """Test creating many entries"""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "perf@example.com",
                "username": "perfuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        login_resp = client.post(
            "/api/v1/auth/login",
            data={
                "username": "perfuser",
                "password": "SecureP@ssw0rd123"
            }
        )
        token = login_resp.json()["access_token"]
        
        # Create 50 entries
        for i in range(50):
            response = client.post(
                "/api/v1/analytics/entries",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "category": "test",
                    "metric": "bulk_test",
                    "value": i
                }
            )
            assert response.status_code == 201


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
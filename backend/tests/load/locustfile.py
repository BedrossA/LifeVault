from locust import HttpUser, task, between

class LifeVaultUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tests"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "SecureP@ssw0rd123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def list_entries(self):
        self.client.get("/api/v1/analytics/entries", headers=self.headers)
    
    @task(1)
    def create_entry(self):
        self.client.post(
            "/api/v1/analytics/entries",
            headers=self.headers,
            json={
                "category": "test",
                "metric": "load_test",
                "value": 100
            }
        )
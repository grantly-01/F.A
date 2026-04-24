"""
Funding Aggregator - Performance Testing with Locust
Run: locust -f locustfile.py --host=http://localhost:8000
"""
from locust import HttpUser, task, between, tag


class FundingAggregatorUser(HttpUser):
    """Simulates a typical user browsing grants."""
    wait_time = between(1, 3)

    def on_start(self):
        """Register and login on start."""
        import uuid
        self.username = f"loadtest_{uuid.uuid4().hex[:8]}"
        
        # Register
        self.client.post("/api/v1/auth/register", json={
            "email": f"{self.username}@test.com",
            "username": self.username,
            "password": "loadtest123456",
        })
        
        # Login
        resp = self.client.post("/api/v1/auth/login", json={
            "username": self.username,
            "password": "loadtest123456",
        })
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @tag("read")
    @task(10)
    def list_grants(self):
        self.client.get("/api/v1/grants/", params={"page": 1, "per_page": 20})

    @tag("read")
    @task(5)
    def search_grants(self):
        self.client.get("/api/v1/grants/", params={"q": "research", "per_page": 10})

    @tag("read")
    @task(3)
    def filter_grants(self):
        self.client.get("/api/v1/grants/", params={
            "country": "United States",
            "status": "active",
            "per_page": 10,
        })

    @tag("read")
    @task(2)
    def get_stats(self):
        self.client.get("/api/v1/grants/stats")

    @tag("read")
    @task(2)
    def get_categories(self):
        self.client.get("/api/v1/grants/categories")

    @tag("read")
    @task(1)
    def health_check(self):
        self.client.get("/health")

    @tag("auth")
    @task(1)
    def get_profile(self):
        if self.headers:
            self.client.get("/api/v1/users/me", headers=self.headers)

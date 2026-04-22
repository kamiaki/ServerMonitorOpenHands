"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_message(self, client):
        """Test that root returns a message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data


class TestMetricsEndpoints:
    """Tests for metrics endpoints."""

    def test_latest_metrics(self, client):
        """Test latest metrics endpoint."""
        response = client.get("/metrics/latest")
        assert response.status_code == 200
        
        data = response.json()
        assert "server_id" in data
        assert "timestamp" in data
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "network" in data

    def test_cpu_metrics(self, client):
        """Test CPU metrics endpoint."""
        response = client.get("/metrics/cpu")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "usage" in data

    def test_memory_metrics(self, client):
        """Test memory metrics endpoint."""
        response = client.get("/metrics/memory")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "total" in data
        assert "available" in data

    def test_disk_metrics(self, client):
        """Test disk metrics endpoint."""
        response = client.get("/metrics/disk")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "partitions" in data

    def test_network_metrics(self, client):
        """Test network metrics endpoint."""
        response = client.get("/metrics/network")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "interfaces" in data

    def test_processes_defaults(self, client):
        """Test process metrics with default params."""
        response = client.get("/metrics/process")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_processes_with_limit(self, client):
        """Test process metrics with limit."""
        response = client.get("/metrics/process?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5

    def test_processes_sort_by_memory(self, client):
        """Test process metrics sorted by memory."""
        response = client.get("/metrics/process?sort_by=memory")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestAPIModels:
    """Tests for API models."""

    def test_latest_metrics_structure(self, client):
        """Test latest metrics response structure."""
        response = client.get("/metrics/latest")
        data = response.json()
        
        # CPU
        assert "usage" in data["cpu"]
        assert "user_mode" in data["cpu"]
        assert "system_mode" in data["cpu"]
        assert "idle" in data["cpu"]
        
        # Memory
        assert "total" in data["memory"]
        assert "available" in data["memory"]
        assert "used" in data["memory"]
        assert "percent" in data["memory"]
        
        # Disk
        assert isinstance(data["disk"], list)
        
        # Network
        assert isinstance(data["network"], list)
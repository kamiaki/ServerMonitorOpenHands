"""Unit tests for collectors."""

import pytest
from collectors.cpu import CPUCollector
from collectors.memory import MemoryCollector
from collectors.disk import DiskCollector
from collectors.network import NetworkCollector
from collectors.process import ProcessCollector
from collectors.base import SystemCollector


class TestCPUCollector:
    """Tests for CPU collector."""

    def test_collect_returns_dict(self):
        """Test that collect returns a dictionary."""
        collector = CPUCollector()
        result = collector.collect()
        assert isinstance(result, dict)

    def test_collect_has_required_fields(self):
        """Test that collect returns required fields."""
        collector = CPUCollector()
        result = collector.collect()
        assert "timestamp" in result
        assert "usage" in result
        assert "user_mode" in result
        assert "system_mode" in result
        assert "idle" in result

    def test_usage_is_percentage(self):
        """Test that usage is a valid percentage."""
        collector = CPUCollector()
        result = collector.collect()
        assert 0 <= result["usage"] <= 100

    def test_idle_plus_usage_equals_100(self):
        """Test that idle + usage ≈ 100."""
        collector = CPUCollector()
        result = collector.collect()
        assert abs(result["usage"] + result["idle"] - 100) < 1


class TestMemoryCollector:
    """Tests for Memory collector."""

    def test_collect_returns_dict(self):
        """Test that collect returns a dictionary."""
        collector = MemoryCollector()
        result = collector.collect()
        assert isinstance(result, dict)

    def test_collect_has_required_fields(self):
        """Test that collect returns required fields."""
        collector = MemoryCollector()
        result = collector.collect()
        assert "timestamp" in result
        assert "total" in result
        assert "available" in result
        assert "used" in result
        assert "percent" in result

    def test_total_equals_available_plus_used(self):
        """Test that total ≈ available + used."""
        collector = MemoryCollector()
        result = collector.collect()
        # Allow some overhead
        assert abs(result["total"] - result["available"] - result["used"]) < 1024 * 1024

    def test_percent_is_valid(self):
        """Test that percent is between 0 and 100."""
        collector = MemoryCollector()
        result = collector.collect()
        assert 0 <= result["percent"] <= 100


class TestDiskCollector:
    """Tests for Disk collector."""

    def test_collect_returns_dict(self):
        """Test that collect returns a dictionary."""
        collector = DiskCollector()
        result = collector.collect()
        assert isinstance(result, dict)

    def test_collect_has_partitions(self):
        """Test that collect returns partitions list."""
        collector = DiskCollector()
        result = collector.collect()
        assert "partitions" in result
        assert isinstance(result["partitions"], list)


class TestNetworkCollector:
    """Tests for Network collector."""

    def test_collect_returns_dict(self):
        """Test that collect returns a dictionary."""
        collector = NetworkCollector()
        result = collector.collect()
        assert isinstance(result, dict)

    def test_collect_has_interfaces(self):
        """Test that collect returns interfaces list."""
        collector = NetworkCollector()
        result = collector.collect()
        assert "interfaces" in result
        assert isinstance(result["interfaces"], list)


class TestProcessCollector:
    """Tests for Process collector."""

    def test_collect_returns_dict(self):
        """Test that collect returns a dictionary."""
        collector = ProcessCollector()
        result = collector.collect()
        assert isinstance(result, dict)

    def test_collect_has_required_fields(self):
        """Test that collect returns required fields."""
        collector = ProcessCollector()
        result = collector.collect()
        assert "timestamp" in result
        assert "count" in result
        assert "processes" in result

    def test_collect_respects_limit(self):
        """Test that collect respects limit parameter."""
        collector = ProcessCollector()
        result = collector.collect(limit=5)
        assert len(result["processes"]) <= 5


class TestSystemCollector:
    """Tests for System collector."""

    def test_initialization(self):
        """Test that SystemCollector initializes correctly."""
        collector = SystemCollector(server_id="test-server")
        assert collector.server_id == "test-server"

    def test_collect_all(self):
        """Test that collect_all returns all metrics."""
        collector = SystemCollector(server_id="test-server")
        result = collector.collect_all()
        
        assert result["server_id"] == "test-server"
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result
        assert "network" in result
        assert "process" in result

    def test_collect_cpu(self):
        """Test collect_cpu method."""
        collector = SystemCollector()
        result = collector.collect_cpu()
        assert "timestamp" in result
        assert "usage" in result

    def test_collect_memory(self):
        """Test collect_memory method."""
        collector = SystemCollector()
        result = collector.collect_memory()
        assert "timestamp" in result
        assert "total" in result

    def test_collect_disk(self):
        """Test collect_disk method."""
        collector = SystemCollector()
        result = collector.collect_disk()
        assert "timestamp" in result
        assert "partitions" in result

    def test_collect_network(self):
        """Test collect_network method."""
        collector = SystemCollector()
        result = collector.collect_network()
        assert "timestamp" in result
        assert "interfaces" in result

    def test_collect_process(self):
        """Test collect_process method."""
        collector = SystemCollector()
        result = collector.collect_process(limit=5)
        assert "timestamp" in result
        assert "processes" in result
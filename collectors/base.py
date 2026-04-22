"""System metrics collector - aggregates all collectors."""

from datetime import datetime
from typing import Dict, Any, Optional

from .cpu import CPUCollector
from .memory import MemoryCollector
from .disk import DiskCollector
from .network import NetworkCollector
from .process import ProcessCollector


class SystemCollector:
    """Aggregates all system metrics collectors."""

    def __init__(self, server_id: str = "local"):
        """Initialize the system collector.

        Args:
            server_id: Server identifier.
        """
        self.server_id = server_id
        self.cpu = CPUCollector()
        self.memory = MemoryCollector()
        self.disk = DiskCollector()
        self.network = NetworkCollector()
        self.process = ProcessCollector()

    def collect_all(self) -> Dict[str, Any]:
        """Collect all system metrics.

        Returns:
            Dictionary containing all system metrics.
        """
        return {
            "server_id": self.server_id,
            "timestamp": datetime.now().isoformat(),
            "cpu": self.cpu.collect(),
            "memory": self.memory.collect(),
            "disk": self.disk.collect(),
            "network": self.network.collect(),
            "process": self.process.collect(),
        }

    def collect_cpu(self) -> Dict[str, Any]:
        """Collect CPU metrics only."""
        return self.cpu.collect()

    def collect_memory(self) -> Dict[str, Any]:
        """Collect memory metrics only."""
        return self.memory.collect()

    def collect_disk(self) -> Dict[str, Any]:
        """Collect disk metrics only."""
        return self.disk.collect()

    def collect_network(self) -> Dict[str, Any]:
        """Collect network metrics only."""
        return self.network.collect()

    def collect_process(self, sort_by: str = "cpu", limit: int = 10) -> Dict[str, Any]:
        """Collect process metrics only."""
        return self.process.collect(sort_by=sort_by, limit=limit)

    def get_process(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get process details by PID."""
        return self.process.get_process_by_pid(pid)
"""Data models for the server monitor API."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CPUMetrics(BaseModel):
    """CPU metrics model."""
    usage: float
    user_mode: float
    system_mode: float
    idle: float
    iowait: float
    per_cpu: Optional[list] = None
    cpu_count: Optional[int] = None


class MemoryMetrics(BaseModel):
    """Memory metrics model."""
    total: int
    available: int
    used: int
    percent: float


class DiskPartition(BaseModel):
    """Disk partition model."""
    device: str
    mount_point: str
    total: int
    used: int
    free: int
    percent: float


class NetworkInterface(BaseModel):
    """Network interface model."""
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class ProcessInfo(BaseModel):
    """Process information model."""
    pid: int
    name: str
    status: str
    cpu_percent: float
    mem_percent: float
    num_threads: int
    cmdline: Optional[str] = None


class LatestMetrics(BaseModel):
    """Latest system metrics model."""
    server_id: str
    timestamp: str
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: List[DiskPartition]
    network: List[NetworkInterface]


class ServerBase(BaseModel):
    """Base server model."""
    server_id: str
    name: str
    description: Optional[str] = None


class ServerCreate(ServerBase):
    """Server creation model."""
    pass


class ServerResponse(ServerBase):
    """Server response model."""
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
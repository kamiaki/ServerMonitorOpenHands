"""Database models for the server monitor."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, BigInteger, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CPUMetric(Base):
    """CPU metrics table model."""
    __tablename__ = "cpu_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    server_id = Column(String(50), nullable=False, index=True)
    usage = Column(Float, nullable=False)
    user_mode = Column(Float)
    system_mode = Column(Float)
    idle = Column(Float)
    iowait = Column(Float)


class MemoryMetric(Base):
    """Memory metrics table model."""
    __tablename__ = "memory_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    server_id = Column(String(50), nullable=False, index=True)
    total = Column(BigInteger, nullable=False)
    available = Column(BigInteger, nullable=False)
    used = Column(BigInteger, nullable=False)
    percent = Column(Float, nullable=False)


class DiskMetric(Base):
    """Disk metrics table model."""
    __tablename__ = "disk_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    server_id = Column(String(50), nullable=False, index=True)
    device = Column(String(100), nullable=False)
    mount_point = Column(String(100), nullable=False)
    total = Column(BigInteger, nullable=False)
    used = Column(BigInteger, nullable=False)
    free = Column(BigInteger, nullable=False)
    percent = Column(Float, nullable=False)


class NetworkMetric(Base):
    """Network metrics table model."""
    __tablename__ = "network_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    server_id = Column(String(50), nullable=False, index=True)
    interface = Column(String(50), nullable=False)
    bytes_sent = Column(BigInteger, nullable=False)
    bytes_recv = Column(BigInteger, nullable=False)
    packets_sent = Column(BigInteger, nullable=False)
    packets_recv = Column(BigInteger, nullable=False)


class ProcessMetric(Base):
    """Process metrics table model."""
    __tablename__ = "process_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(TIMESTAMP(timezone=True), default=datetime.now, nullable=False)
    server_id = Column(String(50), nullable=False, index=True)
    pid = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    cpu_percent = Column(Float, nullable=False)
    mem_percent = Column(Float, nullable=False)
    num_threads = Column(Integer)
    cmdline = Column(Text)


class Server(Base):
    """Server registration table model."""
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now)
    active = Column(Boolean, default=True)
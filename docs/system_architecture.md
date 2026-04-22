# Server Monitor System Architecture

## 1. System Overview

### 1.1 Project Description
**Multi-Agent Linux Server Monitoring System** - 一个基于CrewAI多Agent协作框架开发的服务器监控系统，用于实时监控Linux服务器的CPU、内存、磁盘、网络流量、进程等关键指标。

### 1.2 Design Goals
- **实时性**: 指标采集间隔可配置（默认5秒）
- **可扩展性**: 支持多服务器监控，支持水平扩展
- **可靠性**: 数据持久化存储，支持历史数据查询
- **可视化**: 友好的Web Dashboard实时展示监控数据
- **云就绪**: 支持Docker和Kubernetes部署

---

## 2. System Architecture

### 2.1 Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        Cloud / K8s                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │   Frontend   │◄──│  FastAPI     │◄──│  Collectors  │          │
│  │  (React+TS)  │   │   Backend    │   │   (psutil)    │          │
│  └──────────────┘   └──────────────┘   └──────────────┘          │
│        │                   │                   │                │
│        └───────────────────┼───────────────────┘                │
│                           ▼                                      │
│                  ┌──────────────────┐                           │
│                  │  PostgreSQL +    │                           │
│                  │   TimescaleDB    │                           │
│                  └──────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Components

| Component | Description | Technology |
|-----------|-------------|------------|
| Frontend | 监控仪表盘Web界面 | React + TypeScript + Recharts |
| API | RESTful API服务 | FastAPI + Uvicorn |
| Collector | 系统指标采集器 | psutil |
| Storage | 数据持久化层 | PostgreSQL + TimescaleDB |
| Container | 容器化 | Docker + K8s |

### 2.3 Data Flow
1. **Collector** 每隔5秒采集系统指标（CPU、内存、磁盘、网络、进程）
2. **API** 接收采集数据，存储到 **TimescaleDB**
3. **API** 提供RESTful接口供前端查询
4. **Frontend** 通过WebSocket或轮询获取实时数据并展示

---

## 3. Database Schema

### 3.1 TimescaleDB 时序数据表

```sql
-- 创建CPU指标表
CREATE TABLE IF NOT EXISTS cpu_metrics (
    time        TIMESTAMPTZ       NOT NOW(),
    server_id   VARCHAR(50)       NOT NULL,
    usage       DOUBLE PRECISION NOT NULL,
    user_mode   DOUBLE PRECISION,
    system_mode DOUBLE PRECISION,
    idle        DOUBLE PRECISION,
    iowait      DOUBLE PRECISION
);

-- 创建内存指标表
CREATE TABLE IF NOT EXISTS memory_metrics (
    time           TIMESTAMPTZ       NOT NOW(),
    server_id      VARCHAR(50)       NOT NULL,
    total         BIGINT            NOT NULL,
    available     BIGINT            NOT NULL,
    used          BIGINT            NOT NULL,
    percent       DOUBLE PRECISION  NOT NULL,
    active        BIGINT,
    buffers       BIGINT,
    cached        BIGINT
);

-- 创建磁盘指标表
CREATE TABLE IF NOT EXISTS disk_metrics (
    time        TIMESTAMPTZ       NOT NOW(),
    server_id   VARCHAR(50)       NOT NULL,
    device      VARCHAR(100)       NOT NULL,
    mount_point VARCHAR(100)       NOT NULL,
    total       BIGINT            NOT NULL,
    used        BIGINT            NOT NULL,
    free        BIGINT            NOT NULL,
    percent     DOUBLE PRECISION  NOT NULL
);

-- 创建网络流量表
CREATE TABLE IF NOT EXISTS network_metrics (
    time           TIMESTAMPTZ           NOT NOW(),
    server_id      VARCHAR(50)       NOT NULL,
    interface    VARCHAR(50)        NOT NULL,
    bytes_sent   BIGINT            NOT NULL,
    bytes_recv   BIGINT            NOT NULL,
    packets_sent BIGINT            NOT NULL,
    packets_recv BIGINT            NOT NULL,
    errin        BIGINT            NOT NULL,
    errout       BIGINT            NOT NULL,
    dropin       BIGINT            NOT NULL,
    dropout      BIGINT            NOT NULL
);

-- 创建进程信息表
CREATE TABLE IF NOT EXISTS process_metrics (
    time        TIMESTAMPTZ       NOT NOW(),
    server_id   VARCHAR(50)       NOT NULL,
    pid         INTEGER          NOT NULL,
    name        VARCHAR(100)      NOT NULL,
    status      VARCHAR(20)      NOT NULL,
    cpu_percent DOUBLE PRECISION NOT NULL,
    mem_percent DOUBLE PRECISION NOT NULL,
    num_threads INTEGER,
    cmdline     TEXT
);

-- 转换为超表
SELECT create_hypertable('cpu_metrics', 'time');
SELECT create_hypertable('memory_metrics', 'time');
SELECT create_hypertable('disk_metrics', 'time');
SELECT create_hypertable('network_metrics', 'time');
SELECT create_hypertable('process_metrics', 'time');
```

### 3.2 索引优化
```sql
-- 按server_id和时间范围查询的索引
CREATE INDEX idx_cpu_server_time ON cpu_metrics (server_id, time DESC);
CREATE INDEX idx_memory_server_time ON memory_metrics (server_id, time DESC);
CREATE INDEX idx_disk_server_time ON disk_metrics (server_id, time DESC);
CREATE INDEX idx_network_server_time ON network_metrics (server_id, time DESC);
CREATE INDEX idx_process_server_time ON process_metrics (server_id, time DESC);
CREATE INDEX idx_process_pid ON process_metrics (server_id, pid);
```

---

## 4. API Specification

### 4.1 Base URL
```
http://localhost:8000/api/v1
```

### 4.2 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | 健康检查 |
| GET | `/metrics/latest` | 获取最新指标数据 |
| GET | `/metrics/cpu` | 获取CPU指标 |
| GET | `/metrics/memory` | 获取内存指标 |
| GET | `/metrics/disk` | 获取磁盘指标 |
| GET | `/metrics/network` | 获取网络指标 |
| GET | `/metrics/process` | 获取进程列表 |
| GET | `/metrics/history` | 获取历史指标 |
| POST | `/servers` | 注册服务器 |
| DELETE | `/servers/{server_id}` | 删除服务器 |

### 4.3 API详细规范

#### 4.3.1 GET `/metrics/latest`
返回最新的系统指标数据。

**Response:**
```json
{
    "server_id": "server-001",
    "timestamp": "2024-01-01T00:00:00Z",
    "cpu": {
        "usage": 45.5,
        "user_mode": 30.2,
        "system_mode": 15.3,
        "idle": 54.5,
        "iowait": 0.0
    },
    "memory": {
        "total": 16777216000,
        "available": 8388608000,
        "used": 8388608000,
        "percent": 50.0
    },
    "disk": [
        {
            "device": "/dev/sda1",
            "mount_point": "/",
            "total": 500000000000,
            "used": 250000000000,
            "free": 250000000000,
            "percent": 50.0
        }
    ],
    "network": [
        {
            "interface": "eth0",
            "bytes_sent": 1000000,
            "bytes_recv": 2000000
        }
    ]
}
```

#### 4.3.2 GET `/metrics/history`
返回指定时间范围的指标历史数据。

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| metric_type | string | 指标类型 (cpu, memory, disk, network, process) |
| server_id | string | 服务器ID |
| start_time | datetime | 开始时间 |
| end_time | datetime | 结束时间 |
| interval | string | 聚合间隔 (1m, 5m, 1h, 1d) |
| limit | int | 返回记录数 (默认100) |

#### 4.3.3 GET `/metrics/process`
返回进程列表，按CPU或内存使用率排序。

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| server_id | string | 服务器ID |
| sort_by | string | 排序字段 (cpu, memory) |
| limit | int | 返回记录数 (默认10) |

---

## 5. Data Models (Pydantic)

### 5.1 Metrics Models
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CPUMetrics(BaseModel):
    usage: float
    user_mode: float
    system_mode: float
    idle: float
    iowait: float

class MemoryMetrics(BaseModel):
    total: int
    available: int
    used: int
    percent: float

class DiskMetrics(BaseModel):
    device: str
    mount_point: str
    total: int
    used: int
    free: int
    percent: float

class NetworkMetrics(BaseModel):
    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int

class ProcessMetrics(BaseModel):
    pid: int
    name: str
    status: str
    cpu_percent: float
    mem_percent: float
    num_threads: int
    cmdline: Optional[str]

class LatestMetrics(BaseModel):
    server_id: str
    timestamp: datetime
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: List[DiskMetrics]
    network: List[NetworkMetrics]
```

---

## 6. Configuration

### 6.1 环境变量
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/monitor

# API
API_HOST=0.0.0.0
API_PORT=8000

# Collector
COLLECTION_INTERVAL=5  # seconds
SERVER_ID=server-001

# Frontend
FRONTEND_PORT=3000
```

### 6.2 Docker Compose配置
详见 `docker-compose.yml`

### 6.3 Kubernetes配置
详见 `k8s/` 目录

---

## 7. Deployment

### 7.1 本地开发
```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 单独启动后端
pip install -e .
uvicorn api.main:app --reload
```

### 7.2 生产部署
```bash
# 使用Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 使用Kubernetes
kubectl apply -f k8s/
```

---

## 8. Monitoring Metrics

### 8.1 采集的指标类型

| 指标类型 | 描述 | 采集频率 |
|---------|------|---------|
| CPU | 使用率、用户态/内核态占比、空闲率、IO等待 | 5秒 |
| Memory | 总内存、可用内存、已用内存、使用率 | 5秒 |
| Disk | 各分区总量、已用、可用、使用率 | 30秒 |
| Network | 各网卡流量、收发包数、错误丢包 | 5秒 |
| Process | 进程列表、CPU/内存占用 | 10秒 |

---

## 9. Security Considerations

- API认证：支持API Key和JWT认证
- 数据加密：传输层使用TLS加密
- 权限控制：基于角色的访问控制(RBAC)
- 日志审计：记录所有API访问日志

---

## 10. Future Enhancements

- [ ] 支持告警规则配置
- [ ] 支持Webhook通知
- [ ] 支持Agent自动上报
- [ ] 支持Prometheus导出
- [ ] 支持Grafana集成
- [ ] 支持多租户
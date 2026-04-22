"""FastAPI server monitor application."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.models import (
    LatestMetrics,
    CPUMetrics,
    MemoryMetrics,
    DiskPartition,
    NetworkInterface,
    ProcessInfo,
    ServerCreate,
    ServerResponse,
    HealthResponse,
)
from collectors.base import SystemCollector


# Global collector instance
_collector: Optional[SystemCollector] = None


def get_collector() -> SystemCollector:
    """Get or create the system collector."""
    global _collector
    if _collector is None:
        _collector = SystemCollector(server_id="local")
    return _collector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    global _collector
    _collector = SystemCollector(server_id="local")
    yield
    _collector = None


app = FastAPI(
    title="Server Monitor API",
    description="Multi-Agent Linux Server Monitoring System API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - Beautiful Dashboard HTML page."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Monitor</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-dark: #09090b;
            --bg-card: #18181b;
            --border: #27272a;
            --text: #fafafa;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-green: #22c55e;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
            padding: 24px;
            background-image: 
                radial-gradient(ellipse at 20% 0%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 100%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0 40px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 40px;
        }
        
        .header-left h1 {
            font-size: 28px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .header-left h1 span {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 20px;
            font-size: 13px;
            color: var(--accent-green);
        }
        
        .status-pill::before {
            content: '';
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        .update-time {
            color: var(--text-dim);
            font-size: 13px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }
        
        @media (max-width: 1200px) {
            .grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            border-radius: 20px 20px 0 0;
        }
        
        .card.cpu::before { background: linear-gradient(90deg, var(--accent-blue), #60a5fa); }
        .card.memory::before { background: linear-gradient(90deg, var(--accent-purple), #a78bfa); }
        .card.disk::before { background: linear-gradient(90deg, var(--accent-green), #34d399); }
        .card.network::before { background: linear-gradient(90deg, var(--accent-amber), #fbbf24); }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 14px;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .card.cpu .card-icon { background: rgba(59, 130, 246, 0.15); }
        .card.memory .card-icon { background: rgba(139, 92, 246, 0.15); }
        .card.disk .card-icon { background: rgba(34, 197, 94, 0.15); }
        .card.network .card-icon { background: rgba(245, 158, 11, 0.15); }
        
        .card-value {
            font-size: 42px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 8px;
        }
        
        .card-detail {
            font-size: 13px;
            color: var(--text-dim);
            font-family: 'JetBrains Mono', monospace;
        }
        
        .gauge-container {
            position: relative;
            width: 140px;
            height: 140px;
            margin: 20px auto;
        }
        
        .gauge-svg {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }
        
        .gauge-bg {
            fill: none;
            stroke: var(--border);
            stroke-width: 10;
        }
        
        .gauge-fill {
            fill: none;
            stroke-width: 10;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.5s ease;
        }
        
        .gauge-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        
        .gauge-value {
            font-size: 24px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .gauge-label {
            font-size: 11px;
            color: var(--text-dim);
        }
        
        .chart-container {
            height: 60px;
            margin-top: 16px;
        }
        
        .chart-svg {
            width: 100%;
            height: 100%;
        }
        
        .chart-line {
            fill: none;
            stroke-width: 2;
            stroke-linecap: round;
        }
        
        .chart-area {
            opacity: 0.1;
        }
        
        .processes {
            grid-column: 1 / -1;
        }
        
        .process-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }
        
        .process-table th {
            text-align: left;
            padding: 12px 16px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
        }
        
        .process-table td {
            padding: 14px 16px;
            font-size: 14px;
            border-bottom: 1px solid var(--border);
        }
        
        .process-table tr:last-child td {
            border-bottom: none;
        }
        
        .process-table tbody tr:hover {
            background: rgba(255,255,255,0.02);
        }
        
        .status-badge {
            display: inline-flex;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-running {
            background: rgba(34, 197, 94, 0.15);
            color: var(--accent-green);
        }
        
        .status-sleeping {
            background: rgba(161, 161, 170, 0.15);
            color: var(--text-dim);
        }
        
        .status-zombie {
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
        }
        
        .cpu-bar, .mem-bar {
            width: 50px;
            height: 5px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .cpu-bar-fill, .mem-bar-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .cpu-bar-fill { background: var(--accent-blue); }
        .mem-bar-fill { background: var(--accent-purple); }
        
        .network-stats {
            display: flex;
            gap: 16px;
            margin-top: 16px;
        }
        
        .network-stat {
            flex: 1;
            padding: 12px;
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            text-align: center;
        }
        
        .network-stat-label {
            font-size: 11px;
            color: var(--text-dim);
            margin-bottom: 6px;
        }
        
        .network-stat-value {
            font-size: 14px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .network-stat-value.up { color: var(--accent-green); }
        .network-stat-value.down { color: var(--accent-amber); }
        
        .refresh-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin: 40px auto;
            padding: 14px 28px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .refresh-btn:hover {
            background: var(--border);
            transform: translateY(-2px);
        }
        
        .refresh-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1><span>Server Monitor</span></h1>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="status-pill">Live</div>
            <div class="update-time" id="last-update">--:--:--</div>
        </div>
    </div>
    
    <div class="grid">
        <div class="card cpu">
            <div class="card-header">
                <div class="card-title">CPU</div>
                <div class="card-icon">⚡</div>
            </div>
            <div class="gauge-container">
                <svg class="gauge-svg" viewBox="0 0 140 140">
                    <circle class="gauge-bg" cx="70" cy="70" r="60"/>
                    <circle class="gauge-fill" cx="70" cy="70" r="60" 
                        stroke-dasharray="377" stroke-dashoffset="377" id="cpu-gauge" style="stroke: var(--accent-blue);"/>
                </svg>
                <div class="gauge-text">
                    <div class="gauge-value" id="cpu-value">--%</div>
                    <div class="gauge-label">Usage</div>
                </div>
            </div>
            <div class="card-detail" id="cpu-detail">Loading...</div>
            <div class="chart-container">
                <svg class="chart-svg" viewBox="0 0 200 50" preserveAspectRatio="none">
                    <defs>
                        <linearGradient id="cpuGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
                            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
                        </linearGradient>
                    </defs>
                    <path class="chart-area" id="cpu-area" fill="url(#cpuGrad)"/>
                    <path class="chart-line" id="cpu-chart" stroke="var(--accent-blue)"/>
                </svg>
            </div>
        </div>
        
        <div class="card memory">
            <div class="card-header">
                <div class="card-title">Memory</div>
                <div class="card-icon">💾</div>
            </div>
            <div class="gauge-container">
                <svg class="gauge-svg" viewBox="0 0 140 140">
                    <circle class="gauge-bg" cx="70" cy="70" r="60"/>
                    <circle class="gauge-fill" cx="70" cy="70" r="60" 
                        stroke-dasharray="377" stroke-dashoffset="377" id="mem-gauge" style="stroke: var(--accent-purple);"/>
                </svg>
                <div class="gauge-text">
                    <div class="gauge-value" id="mem-value">--%</div>
                    <div class="gauge-label">Usage</div>
                </div>
            </div>
            <div class="card-detail" id="mem-detail">Loading...</div>
        </div>
        
        <div class="card disk">
            <div class="card-header">
                <div class="card-title">Disk</div>
                <div class="card-icon">📦</div>
            </div>
            <div class="gauge-container">
                <svg class="gauge-svg" viewBox="0 0 140 140">
                    <circle class="gauge-bg" cx="70" cy="70" r="60"/>
                    <circle class="gauge-fill" cx="70" cy="70" r="60" 
                        stroke-dasharray="377" stroke-dashoffset="377" id="disk-gauge" style="stroke: var(--accent-green);"/>
                </svg>
                <div class="gauge-text">
                    <div class="gauge-value" id="disk-value">--%</div>
                    <div class="gauge-label">Usage</div>
                </div>
            </div>
            <div class="card-detail" id="disk-detail">Loading...</div>
        </div>
        
        <div class="card network">
            <div class="card-header">
                <div class="card-title">Network</div>
                <div class="card-icon">📡</div>
            </div>
            <div class="card-value" id="net-value" style="font-size: 28px;">--</div>
            <div class="card-detail" id="net-detail">Loading...</div>
            <div class="network-stats">
                <div class="network-stat">
                    <div class="network-stat-label">Sent</div>
                    <div class="network-stat-value up" id="net-sent">--</div>
                </div>
                <div class="network-stat">
                    <div class="network-stat-label">Received</div>
                    <div class="network-stat-value down" id="net-recv">--</div>
                </div>
            </div>
        </div>
        
        <div class="card processes">
            <div class="card-header">
                <div class="card-title">Top Processes</div>
            </div>
            <table class="process-table">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>CPU</th>
                        <th>Memory</th>
                    </tr>
                </thead>
                <tbody id="process-body">
                    <tr><td colspan="5" style="text-align: center; padding: 30px; color: var(--text-dim);">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <button class="refresh-btn" id="refresh-btn" onclick="fetchMetrics()">
        Refresh Metrics
    </button>
    
    <script>
    const cpuHistory = [];
    const MAX_HISTORY = 20;
    const circumference = 2 * Math.PI * 60;
    
    function formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
    }
    
    function updateGauge(id, value) {
        const offset = circumference - (value / 100) * circumference;
        document.getElementById(id).style.strokeDashoffset = offset;
    }
    
    function updateChart(history, lineId, areaId) {
        if (history.length < 2) return;
        const width = 200, height = 50, pad = 5;
        const min = Math.min(...history), max = Math.max(...history, 100);
        const range = max - min || 1;
        const points = history.map((v, i) => {
            const x = (i / (MAX_HISTORY - 1)) * width;
            const y = height - ((v - min) / range) * (height - pad * 2) - pad;
            return x + ',' + y;
        });
        document.getElementById(lineId).setAttribute('d', 'M' + points.join(' L'));
        document.getElementById(areaId).setAttribute('d', 'M' + points.join(' L') + ' L' + width + ',' + height + ' L0,' + height + ' Z');
    }
    
    async function fetchMetrics() {
        const btn = document.getElementById('refresh-btn');
        btn.disabled = true;
        btn.textContent = 'Loading...';
        
        try {
            const [latestRes, procRes] = await Promise.all([
                fetch('/metrics/latest').then(r => r.json()),
                fetch('/metrics/process?limit=8').then(r => r.json())
            ]);
            
            const now = new Date();
            document.getElementById('last-update').textContent = now.toLocaleTimeString();
            
            const cpu = latestRes.cpu;
            cpuHistory.push(cpu.usage);
            if (cpuHistory.length > MAX_HISTORY) cpuHistory.shift();
            
            updateGauge('cpu-gauge', cpu.usage);
            document.getElementById('cpu-value').textContent = cpu.usage.toFixed(1) + '%';
            document.getElementById('cpu-detail').textContent = 
                'User: ' + cpu.user_mode.toFixed(1) + '% | System: ' + cpu.system_mode.toFixed(1) + '%';
            updateChart(cpuHistory, 'cpu-chart', 'cpu-area');
            
            const mem = latestRes.memory;
            updateGauge('mem-gauge', mem.percent);
            document.getElementById('mem-value').textContent = mem.percent.toFixed(1) + '%';
            document.getElementById('mem-detail').textContent = formatBytes(mem.used) + ' / ' + formatBytes(mem.total);
            
            if (latestRes.disk && latestRes.disk.length > 0) {
                const disk = latestRes.disk.find(d => d.mount_point === '/workspace') || latestRes.disk[0];
                updateGauge('disk-gauge', disk.percent);
                document.getElementById('disk-value').textContent = disk.percent.toFixed(1) + '%';
                document.getElementById('disk-detail').textContent = formatBytes(disk.used) + ' / ' + formatBytes(disk.total);
            }
            
            if (latestRes.network && latestRes.network.length > 0) {
                const net = latestRes.network.find(n => n.interface !== 'lo') || latestRes.network[0];
                document.getElementById('net-value').textContent = net.interface;
                document.getElementById('net-detail').textContent = 'Total: ' + formatBytes(net.bytes_sent + net.bytes_recv);
                document.getElementById('net-sent').textContent = formatBytes(net.bytes_sent);
                document.getElementById('net-recv').textContent = formatBytes(net.bytes_recv);
            }
            
            const tbody = document.getElementById('process-body');
            tbody.innerHTML = procRes.slice(0, 8).map(p => {
                let statusClass = 'status-sleeping';
                if (p.status === 'running' || p.status === 'run') statusClass = 'status-running';
                else if (p.status === 'zombie') statusClass = 'status-zombie';
                
                return '<tr>' +
                    '<td>' + p.pid + '</td>' +
                    '<td style="font-family: JetBrains Mono, monospace;">' + p.name + '</td>' +
                    '<td><span class="status-badge ' + statusClass + '">' + p.status + '</span></td>' +
                    '<td><div class="cpu-bar"><div class="cpu-bar-fill" style="width: ' + Math.min(100, p.cpu_percent) + '%"></div></div></td>' +
                    '<td><div class="mem-bar"><div class="mem-bar-fill" style="width: ' + Math.min(100, p.mem_percent) + '%"></div></div></td>' +
                '</tr>';
            }).join('');
            
        } catch (e) {
            console.error('Error:', e);
        }
        
        btn.disabled = false;
        btn.textContent = 'Refresh Metrics';
    }
    
    fetchMetrics();
    setInterval(fetchMetrics, 5000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0", timestamp=datetime.now().isoformat())


@app.get("/metrics/latest", response_model=LatestMetrics, tags=["Metrics"])
async def get_latest_metrics(server_id: str = Query("local", alias="server-id")):
    """Get latest system metrics."""
    collector = get_collector()
    result = collector.collect_all()
    # Convert dict to model format
    return {
        "server_id": "local",
        "timestamp": result.get("timestamp", datetime.now().isoformat()),
        "cpu": result.get("cpu", {}),
        "memory": result.get("memory", {}),
        "disk": result.get("disk", {}).get("partitions", []) if isinstance(result.get("disk"), dict) else result.get("disk", []),
        "network": result.get("network", {}).get("interfaces", []) if isinstance(result.get("network"), dict) else result.get("network", []),
    }


@app.get("/metrics/cpu", response_model=CPUMetrics, tags=["Metrics"])
async def get_cpu_metrics():
    """Get CPU metrics."""
    collector = get_collector()
    result = collector.collect_all()
    return result.get("cpu", {})


@app.get("/metrics/memory", response_model=MemoryMetrics, tags=["Metrics"])
async def get_memory_metrics():
    """Get memory metrics."""
    collector = get_collector()
    result = collector.collect_all()
    return result.get("memory", {})


@app.get("/metrics/disk", response_model=List[DiskPartition], tags=["Metrics"])
async def get_disk_metrics():
    """Get disk metrics."""
    collector = get_collector()
    metrics = collector.collect_all()
    result = metrics.get("disk", {})
    if isinstance(result, dict):
        return result.get("partitions", [])
    return result


@app.get("/metrics/network", response_model=List[NetworkInterface], tags=["Metrics"])
async def get_network_metrics():
    """Get network metrics."""
    collector = get_collector()
    metrics = collector.collect_all()
    result = metrics.get("network", {})
    if isinstance(result, dict):
        return result.get("interfaces", [])
    return result


@app.get("/metrics/process", response_model=List[ProcessInfo], tags=["Metrics"])
async def get_process_metrics(limit: int = Query(10, ge=1, le=100)):
    """Get process metrics."""
    collector = get_collector()
    result = collector.collect_process()
    # Handle both dict and list return formats
    if isinstance(result, dict):
        processes = result.get("processes", [])
    else:
        processes = result
    return processes[:limit]


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
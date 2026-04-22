import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// Types
interface CPUMetrics {
  usage: number
  user_mode: number
  system_mode: number
  idle: number
  iowait: number
}

interface MemoryMetrics {
  total: number
  available: number
  used: number
  percent: number
}

interface DiskPartition {
  device: string
  mount_point: string
  total: number
  used: number
  free: number
  percent: number
}

interface NetworkInterface {
  interface: string
  bytes_sent: number
  bytes_recv: number
  packets_sent: number
  packets_recv: number
}

interface ProcessInfo {
  pid: number
  name: string
  status: string
  cpu_percent: number
  mem_percent: number
  num_threads: number
}

interface MetricsData {
  server_id: string
  timestamp: string
  cpu: CPUMetrics
  memory: MemoryMetrics
  disk: DiskPartition[]
  network: NetworkInterface[]
}

const API_URL = '/api/v1'

// Utility functions
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatPercent(value: number): string {
  return value.toFixed(1) + '%'
}

export default function App() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [processes, setProcesses] = useState<ProcessInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const fetchMetrics = async () => {
    try {
      const [metricsRes, processRes] = await Promise.all([
        axios.get(`${API_URL}/metrics/latest`),
        axios.get(`${API_URL}/metrics/process?limit=10`)
      ])
      setMetrics(metricsRes.data)
      setProcesses(processRes.data)
      setLastUpdate(new Date())
      setError(null)
      setLoading(false)
    } catch (err) {
      setError('Failed to fetch metrics')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading metrics...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error">
        <p>⚠️ {error}</p>
        <button onClick={fetchMetrics}>Retry</button>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-content">
          <h1>🖥️ Server Monitor</h1>
          <div className="header-info">
            <span className="server-id">{metrics?.server_id || 'local'}</span>
            <span className="last-update">
              Last update: {lastUpdate?.toLocaleTimeString() || 'N/A'}
            </span>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="metrics-grid">
          {/* CPU Card */}
          <div className="metric-card cpu">
            <h2>💻 CPU Usage</h2>
            <div className="metric-value">{formatPercent(metrics?.cpu.usage || 0)}</div>
            <div className="metric-bar">
              <div 
                className="metric-bar-fill cpu" 
                style={{ width: `${metrics?.cpu.usage || 0}%` }}
              ></div>
            </div>
            <div className="metric-details">
              <div>User: {formatPercent(metrics?.cpu.user_mode || 0)}</div>
              <div>System: {formatPercent(metrics?.cpu.system_mode || 0)}</div>
              <div>Idle: {formatPercent(metrics?.cpu.idle || 0)}</div>
            </div>
          </div>

          {/* Memory Card */}
          <div className="metric-card memory">
            <h2>🧠 Memory</h2>
            <div className="metric-value">{formatPercent(metrics?.memory.percent || 0)}</div>
            <div className="metric-bar">
              <div 
                className="metric-bar-fill memory" 
                style={{ width: `${metrics?.memory.percent || 0}%` }}
              ></div>
            </div>
            <div className="metric-details">
              <div>Used: {formatBytes(metrics?.memory.used || 0)}</div>
              <div>Available: {formatBytes(metrics?.memory.available || 0)}</div>
              <div>Total: {formatBytes(metrics?.memory.total || 0)}</div>
            </div>
          </div>

          {/* Disk Card */}
          <div className="metric-card disk">
            <h2>💾 Disk</h2>
            {metrics?.disk.map((d, i) => (
              <div key={i} className="disk-partition">
                <div className="disk-mount">{d.mount_point}</div>
                <div className="metric-value">{formatPercent(d.percent)}</div>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill disk" 
                    style={{ width: `${d.percent}%` }}
                  ></div>
                </div>
                <div className="metric-details">
                  <div>{formatBytes(d.used)} / {formatBytes(d.total)}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Network Card */}
          <div className="metric-card network">
            <h2>🌐 Network</h2>
            {metrics?.network.slice(0, 3).map((n, i) => (
              <div key={i} className="network-iface">
                <div className="network-name">{n.interface}</div>
                <div className="network-stats">
                  <span>↑ {formatBytes(n.bytes_sent)}</span>
                  <span>↓ {formatBytes(n.bytes_recv)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Processes Table */}
        <div className="processes-section">
          <h2>⚙️ Top Processes</h2>
          <div className="processes-table">
            <table>
              <thead>
                <tr>
                  <th>PID</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>CPU %</th>
                  <th>Memory %</th>
                  <th>Threads</th>
                </tr>
              </thead>
              <tbody>
                {processes.map((p) => (
                  <tr key={p.pid}>
                    <td>{p.pid}</td>
                    <td>{p.name}</td>
                    <td>
                      <span className={`status ${p.status.toLowerCase()}`}>
                        {p.status}
                      </span>
                    </td>
                    <td>{formatPercent(p.cpu_percent)}</td>
                    <td>{formatPercent(p.mem_percent)}</td>
                    <td>{p.num_threads}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
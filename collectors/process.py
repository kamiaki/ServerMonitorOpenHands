"""Process metrics collector."""

import psutil
from datetime import datetime
from typing import Dict, Any, List


class ProcessCollector:
    """Collects process metrics from the system."""

    def collect(self, sort_by: str = "cpu", limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Collect process metrics.

        Args:
            sort_by: Sort by 'cpu' or 'memory'.
            limit: Number of processes to return.

        Returns:
            Dictionary containing process metrics.
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'num_threads', 'cmdline']):
            try:
                pinfo = proc.info
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "status": pinfo['status'],
                    "cpu_percent": pinfo['cpu_percent'] or 0.0,
                    "mem_percent": pinfo['memory_percent'] or 0.0,
                    "num_threads": pinfo['num_threads'] or 0,
                    "cmdline": ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else '',
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                continue

        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        else:
            processes.sort(key=lambda x: x['mem_percent'], reverse=True)

        # Get system-wide process count
        count = len(processes)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "count": count,
            "processes": processes[:limit],
        }

    def get_process_by_pid(self, pid: int) -> Dict[str, Any]:
        """Get process details by PID."""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "create_time": proc.create_time(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "memory_info": proc.memory_info()._asdict(),
                    "num_threads": proc.num_threads(),
                    "cmdline": proc.cmdline(),
                    "exe": proc.exe(),
                    "cwd": proc.cwd(),
                    "username": proc.username(),
                }
        except psutil.NoSuchProcess:
            return {"error": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"error": "Access denied"}
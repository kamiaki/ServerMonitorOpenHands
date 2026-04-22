"""CPU metrics collector."""

import psutil
from datetime import datetime
from typing import Dict, Any


class CPUCollector:
    """Collects CPU metrics from the system."""

    def collect(self) -> Dict[str, Any]:
        """Collect CPU metrics.

        Returns:
            Dictionary containing CPU metrics.
        """
        cpu_times = psutil.cpu_times()
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=False)
        cpu_percent_per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_stats = psutil.cpu_stats()
        
        # Get CPU frequencies
        try:
            cpu_freq = psutil.cpu_freq()
            freq = {
                "current": cpu_freq.current if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0,
            }
        except Exception:
            freq = {"current": 0, "min": 0, "max": 0}

        # Calculate per-mode percentages
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        user_mode = sum(per_cpu) / len(per_cpu) if per_cpu else 0
        system_mode = cpu_percent - user_mode
        
        return {
            "timestamp": datetime.now().isoformat(),
            "usage": cpu_percent,
            "user_mode": user_mode,
            "system_mode": system_mode,
            "idle": 100 - cpu_percent,
            "iowait": 0.0,
            "per_cpu": cpu_percent_per_cpu,
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "stats": {
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls,
            },
            "freq": freq,
        }
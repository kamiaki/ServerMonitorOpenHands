"""Disk metrics collector."""

import psutil
from datetime import datetime
from typing import Dict, Any, List


class DiskCollector:
    """Collects disk metrics from the system."""

    def collect(self) -> Dict[str, Any]:
        """Collect disk metrics.

        Returns:
            Dictionary containing disk metrics.
        """
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mount_point": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except PermissionError:
                # Skip partitions we don't have permission to access
                continue
            except OSError:
                # Skip mount points that no longer exist
                continue

        # Disk I/O statistics
        disk_io = psutil.disk_io_counters()
        io_stats = {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
            "read_time": disk_io.read_time,
            "write_time": disk_io.write_time,
        } if disk_io else None

        return {
            "timestamp": datetime.now().isoformat(),
            "partitions": partitions,
            "io": io_stats,
        }
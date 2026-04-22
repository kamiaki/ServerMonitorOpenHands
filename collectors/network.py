"""Network metrics collector."""

import psutil
from datetime import datetime
from typing import Dict, Any, List


class NetworkCollector:
    """Collects network metrics from the system."""

    def collect(self) -> Dict[str, Any]:
        """Collect network metrics.

        Returns:
            Dictionary containing network metrics.
        """
        net_io = psutil.net_io_counters()
        interfaces = []
        
        for interface, stats in psutil.net_io_counters(pernic=True).items():
            interfaces.append({
                "interface": interface,
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv,
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "errin": stats.errin,
                "errout": stats.errout,
                "dropin": stats.dropin,
                "dropout": stats.dropout,
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "total": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
            },
            "interfaces": interfaces,
        }
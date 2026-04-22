"""Memory metrics collector."""

import psutil
from datetime import datetime
from typing import Dict, Any


class MemoryCollector:
    """Collects memory metrics from the system."""

    def collect(self) -> Dict[str, Any]:
        """Collect memory metrics.

        Returns:
            Dictionary containing memory metrics.
        """
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "timestamp": datetime.now().isoformat(),
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "free": vm.free,
            "percent": vm.percent,
            "active": vm.active,
            "inactive": vm.inactive,
            "buffers": getattr(vm, 'buffers', 0),
            "cached": getattr(vm, 'cached', 0),
            "shared": getattr(vm, 'shared', 0),
            "swap": {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": swap.sin,
                "sout": swap.sout,
            },
        }
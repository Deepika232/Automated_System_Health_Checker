from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

cpu_gauge = Gauge("system_cpu_percent", "System CPU usage percent")
mem_gauge = Gauge("system_memory_percent", "System memory usage percent")
disk_gauge = Gauge("system_disk_percent", "System disk usage percent")
uptime_gauge = Gauge("system_uptime_seconds", "System uptime in seconds")


def export_metrics(cpu: float, mem: float, disk: float, uptime: int) -> None:
    cpu_gauge.set(cpu)
    mem_gauge.set(mem)
    disk_gauge.set(disk)
    uptime_gauge.set(uptime)


def prometheus_response():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

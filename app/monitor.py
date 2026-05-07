from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass

import psutil

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MetricSnapshot:
    cpu_percent: float
    mem_percent: float
    disk_percent: float
    uptime_seconds: int
    hostname: str
    platform: str
    timestamp: int


def _uptime_seconds() -> int:
    boot = psutil.boot_time()
    return int(time.time() - boot)


def get_basic_metrics() -> MetricSnapshot:
    cpu = float(psutil.cpu_percent(interval=0.2))
    mem = float(psutil.virtual_memory().percent)
    disk = float(psutil.disk_usage(os.getenv("DISK_PATH", "/")).percent)
    return MetricSnapshot(
        cpu_percent=cpu,
        mem_percent=mem,
        disk_percent=disk,
        uptime_seconds=_uptime_seconds(),
        hostname=platform.node(),
        platform=f"{platform.system()} {platform.release()}",
        timestamp=int(time.time()),
    )


def get_running_services(service_names: list[str]) -> dict[str, str]:
    """
    Linux-focused service check via systemctl (best-effort).
    Returns mapping: service -> status string.
    """
    statuses: dict[str, str] = {}
    if shutil.which("systemctl") is None:
        for s in service_names:
            statuses[s] = "unknown (systemctl not available)"
        return statuses

    for s in service_names:
        try:
            r = subprocess.run(
                ["systemctl", "is-active", s],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            out = (r.stdout or r.stderr).strip() or "unknown"
            statuses[s] = out
        except Exception:
            logger.exception("Service check failed for %s", s)
            statuses[s] = "unknown (error)"
    return statuses


def get_docker_containers() -> dict[str, str]:
    """
    Best-effort Docker status (requires docker CLI in runtime).
    Returns mapping: container_name -> status.
    """
    if shutil.which("docker") is None:
        return {"docker": "not available"}

    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
        if not lines:
            return {"docker": "no running containers"}
        out: dict[str, str] = {}
        for ln in lines:
            if "|" in ln:
                name, status = ln.split("|", 1)
                out[name] = status
        return out or {"docker": "unknown"}
    except Exception:
        logger.exception("Docker status check failed.")
        return {"docker": "unknown (error)"}


def evaluate_alerts(settings: Settings, snap: MetricSnapshot) -> list[str]:
    alerts: list[str] = []
    if snap.cpu_percent > settings.cpu_threshold_percent:
        alerts.append(f"ALERT: CPU usage high ({snap.cpu_percent:.1f}% > {settings.cpu_threshold_percent:.0f}%)")
    if snap.mem_percent > settings.mem_threshold_percent:
        alerts.append(
            f"ALERT: Memory usage high ({snap.mem_percent:.1f}% > {settings.mem_threshold_percent:.0f}%)"
        )
    if snap.disk_percent > settings.disk_threshold_percent:
        alerts.append(
            f"ALERT: Disk usage high ({snap.disk_percent:.1f}% > {settings.disk_threshold_percent:.0f}%)"
        )
    return alerts


def write_health_report(
    settings: Settings,
    snap: MetricSnapshot,
    services: dict[str, str],
    docker_status: dict[str, str],
    alerts: list[str],
) -> str:
    os.makedirs(os.path.dirname(settings.report_path) or ".", exist_ok=True)

    lines: list[str] = []
    lines.append("AUTOMATED SYSTEM HEALTH CHECKER - HEALTH REPORT")
    lines.append("=" * 55)
    lines.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snap.timestamp))}")
    lines.append(f"Host: {snap.hostname}")
    lines.append(f"Platform: {snap.platform}")
    lines.append("")
    lines.append(f"CPU Usage:   {snap.cpu_percent:.1f}%")
    lines.append(f"RAM Usage:   {snap.mem_percent:.1f}%")
    lines.append(f"Disk Usage:  {snap.disk_percent:.1f}%")
    lines.append(f"Uptime:      {snap.uptime_seconds} seconds")
    lines.append("")
    lines.append("Running Services:")
    for name, status in services.items():
        lines.append(f"- {name}: {status}")
    lines.append("")
    lines.append("Docker Container Status:")
    for name, status in docker_status.items():
        lines.append(f"- {name}: {status}")
    lines.append("")
    lines.append("Alerts:")
    if alerts:
        for a in alerts:
            lines.append(f"- {a}")
    else:
        lines.append("- No alerts. All metrics within thresholds.")
    lines.append("")
    lines.append("Raw JSON Snapshot:")
    lines.append(json.dumps(asdict(snap), indent=2))
    lines.append("")

    content = "\n".join(lines)
    with open(settings.report_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Health report written to %s", settings.report_path)
    return settings.report_path

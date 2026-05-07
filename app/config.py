from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    # Thresholds
    cpu_threshold_percent: float = float(os.getenv("CPU_THRESHOLD", "80"))
    mem_threshold_percent: float = float(os.getenv("MEM_THRESHOLD", "80"))
    disk_threshold_percent: float = float(os.getenv("DISK_THRESHOLD", "80"))

    # Report/log paths
    report_path: str = os.getenv("HEALTH_REPORT_PATH", "reports/health_report.txt")
    log_path: str = os.getenv("LOG_PATH", "logs/app.log")

    # Email alerts (optional)
    smtp_host: str | None = os.getenv("SMTP_HOST") or None
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER") or None
    smtp_password: str | None = os.getenv("SMTP_PASSWORD") or None
    smtp_from: str | None = os.getenv("SMTP_FROM") or None
    alert_to: str | None = os.getenv("ALERT_TO") or None
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

    # Docker/service checks
    service_names: list[str] = field(
        default_factory=lambda: [
            s.strip()
            for s in os.getenv("SERVICE_NAMES", "ssh,cron,docker").split(",")
            if s.strip()
        ]
    )

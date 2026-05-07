from __future__ import annotations

import logging

from flask import Blueprint, current_app, jsonify, render_template

from app.alerts import send_email_alert
from app.metrics import export_metrics, prometheus_response
from app.monitor import (
    evaluate_alerts,
    get_basic_metrics,
    get_docker_containers,
    get_running_services,
    write_health_report,
)

logger = logging.getLogger(__name__)

bp = Blueprint("health", __name__)


def _snapshot_payload():
    settings = current_app.config["SETTINGS"]
    snap = get_basic_metrics()
    export_metrics(snap.cpu_percent, snap.mem_percent, snap.disk_percent, snap.uptime_seconds)
    alerts = evaluate_alerts(settings, snap)
    return settings, snap, alerts


@bp.get("/")
def dashboard():
    return render_template("index.html")


@bp.get("/health")
def health():
    settings, snap, alerts = _snapshot_payload()
    services = get_running_services(settings.service_names)
    docker_status = get_docker_containers()

    report_path = write_health_report(settings, snap, services, docker_status, alerts)
    if alerts:
        subject = f"[ALERT] System Health Issues on {snap.hostname}"
        body = "\n".join(alerts) + f"\n\nReport: {report_path}"
        send_email_alert(settings, subject=subject, body=body)

    return jsonify(
        status="ok" if not alerts else "degraded",
        cpu_percent=snap.cpu_percent,
        memory_percent=snap.mem_percent,
        disk_percent=snap.disk_percent,
        uptime_seconds=snap.uptime_seconds,
        hostname=snap.hostname,
        alerts=alerts,
        services=services,
        docker=docker_status,
        report_path=report_path,
    )


@bp.get("/cpu")
def cpu():
    _, snap, _ = _snapshot_payload()
    return jsonify(cpu_percent=snap.cpu_percent)


@bp.get("/memory")
def memory():
    _, snap, _ = _snapshot_payload()
    return jsonify(memory_percent=snap.mem_percent)


@bp.get("/disk")
def disk():
    _, snap, _ = _snapshot_payload()
    return jsonify(disk_percent=snap.disk_percent)


@bp.get("/metrics")
def metrics():
    return prometheus_response()

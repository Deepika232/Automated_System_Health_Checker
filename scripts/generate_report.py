from __future__ import annotations

import os
import sys

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app.config import Settings  # noqa: E402
from app.logging_setup import setup_logging  # noqa: E402
from app.monitor import (  # noqa: E402
    evaluate_alerts,
    get_basic_metrics,
    get_docker_containers,
    get_running_services,
    write_health_report,
)


def main() -> int:
    settings = Settings()
    setup_logging(settings.log_path)

    snap = get_basic_metrics()
    alerts = evaluate_alerts(settings, snap)
    services = get_running_services(settings.service_names)
    docker_status = get_docker_containers()
    write_health_report(settings, snap, services, docker_status, alerts)

    if alerts:
        print("\n".join(alerts))
        return 2
    print("OK: Report generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


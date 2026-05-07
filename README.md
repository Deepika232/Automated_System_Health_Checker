# AUTOMATED SYSTEM HEALTH CHECKER

Beginner-friendly, **resume-worthy DevOps project** that monitors CPU/RAM/Disk/Uptime, checks services and Docker status, generates a report file, exposes REST APIs, provides a modern Flask dashboard, and integrates **Prometheus + Grafana** with CI/CD via **Jenkins + GitHub Actions**.

## Architecture (diagram)

```text
                   ┌──────────────────────────┐
                   │   Jenkins / GitHub CI    │
                   │  (lint, tests, build)    │
                   └───────────┬──────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                       Docker Compose Network                   │
│                                                               │
│  ┌───────────────┐     scrape /metrics     ┌────────────────┐ │
│  │   Flask App    │◄───────────────────────│   Prometheus    │ │
│  │ (Dashboard+API)│                         └───────┬────────┘ │
│  │  /health etc.  │                                 │          │
│  │  /metrics      │                                 │ query    │
│  └───────┬────────┘                                 ▼          │
│          │                                   ┌────────────────┐ │
│          │ dashboards                         │    Grafana     │ │
│          └──────────────────────────────────► │ (provisioned)  │ │
│                                              └────────────────┘ │
└───────────────────────────────────────────────────────────────┘

Host checks:
- psutil for CPU/RAM/Disk/Uptime
- systemctl (best-effort) for service status
- docker CLI (best-effort) for container status

Outputs:
- `reports/health_report.txt`
- `logs/app.log`
```

## Features

- **Auto monitoring**: CPU usage, RAM usage, disk usage, system uptime
- **Checks**: running services (Linux/systemd best-effort), Docker container status (best-effort)
- **Threshold alerts**: CPU/RAM/Disk > 80% → alert messages
- **Auto health report**: writes `reports/health_report.txt`
- **Flask dashboard**: modern UI, auto-refresh every 5 seconds
- **REST API**:
  - `GET /health`
  - `GET /cpu`
  - `GET /memory`
  - `GET /disk`
- **Prometheus metrics**: `GET /metrics`
- **Grafana dashboard**: provisioned automatically on container startup
- **Logging**: `logs/app.log` with rotation
- **Email alerts**: SMTP (optional via env vars)

## Project Structure

```text
AUTOMATED_SYSTEM_HEALTH_CHECKER/
├── app/
├── scripts/
├── reports/
├── logs/
├── prometheus/
├── grafana/
├── tests/
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Setup (local, without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open:
- Dashboard: `http://localhost:5000/`
- Health API: `http://localhost:5000/health`
- Prometheus metrics: `http://localhost:5000/metrics`

## Setup (Docker + Prometheus + Grafana)

```bash
docker compose up --build
```

Open:
- Flask dashboard: `http://localhost:5000/`
- Prometheus: `http://localhost:9090/`
- Grafana: `http://localhost:3000/` (user: `admin`, pass: `admin`)

## Generate Health Report (script)

- **Python report generator** (writes `reports/health_report.txt`):

```bash
python scripts/generate_report.py
```

- **Bash health check wrapper** (calls `/health`):

```bash
APP_URL=http://localhost:5000/health ./scripts/health_check.sh
```

## Email Alerts (optional)

Copy `.env.example` to `.env` and fill SMTP values:

```bash
cp .env.example .env
```

Environment variables used:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `ALERT_TO`, `SMTP_USE_TLS`

## CI/CD Explanation

### GitHub Actions (`.github/workflows/ci.yml`)

- Runs on every push
- Installs dependencies
- Runs **ruff** lint checks
- Runs **pytest**
- Builds Docker image to ensure Dockerfile works

### Jenkins (`Jenkinsfile`)

Stages:
- Clone repo
- Install dependencies (venv)
- Run tests
- Build Docker image
- Run container
- Deploy (placeholder stage for your environment)

## Sample Alert Messages

- `ALERT: CPU usage high (92.1% > 80%)`
- `ALERT: Memory usage high (85.3% > 80%)`
- `ALERT: Disk usage high (91.7% > 80%)`

## Sample API Responses

### `GET /health`

```json
{
  "status": "degraded",
  "cpu_percent": 92.1,
  "memory_percent": 85.3,
  "disk_percent": 44.2,
  "uptime_seconds": 12345,
  "hostname": "my-host",
  "alerts": ["ALERT: CPU usage high (92.1% > 80%)"],
  "services": {"docker": "active", "ssh": "active"},
  "docker": {"docker": "no running containers"},
  "report_path": "reports/health_report.txt"
}
```

### `GET /cpu`

```json
{ "cpu_percent": 23.4 }
```


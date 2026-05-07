from __future__ import annotations


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data
    assert "alerts" in data


def test_metric_endpoints(client):
    assert client.get("/cpu").status_code == 200
    assert client.get("/memory").status_code == 200
    assert client.get("/disk").status_code == 200


def test_metrics_prometheus(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.data.decode("utf-8", errors="ignore")
    assert "system_cpu_percent" in body


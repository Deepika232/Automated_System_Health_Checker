const $ = (id) => document.getElementById(id);

function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

function barColor(pct) {
  if (pct >= 90) return "linear-gradient(90deg, var(--bad), var(--warn))";
  if (pct >= 80) return "linear-gradient(90deg, var(--warn), var(--accent))";
  return "linear-gradient(90deg, var(--good), var(--accent))";
}

function setBar(el, pct) {
  const v = clamp(pct, 0, 100);
  el.style.width = `${v}%`;
  el.style.background = barColor(v);
}

function setStatusPill(status) {
  const pill = $("statusPill");
  pill.textContent = status === "ok" ? "Healthy" : "Degraded";
  pill.style.color = status === "ok" ? "var(--good)" : "var(--warn)";
}

function renderAlerts(alerts) {
  const ul = $("alerts");
  ul.innerHTML = "";
  if (!alerts || alerts.length === 0) {
    const li = document.createElement("li");
    li.className = "muted";
    li.textContent = "No alerts. All metrics within thresholds.";
    ul.appendChild(li);
    return;
  }
  for (const a of alerts) {
    const li = document.createElement("li");
    li.textContent = a;
    ul.appendChild(li);
  }
}

async function refresh() {
  try {
    const res = await fetch("/health", { cache: "no-store" });
    const data = await res.json();

    const cpu = Number(data.cpu_percent ?? 0);
    const mem = Number(data.memory_percent ?? 0);
    const disk = Number(data.disk_percent ?? 0);

    $("cpu").textContent = `${cpu.toFixed(1)}%`;
    $("mem").textContent = `${mem.toFixed(1)}%`;
    $("disk").textContent = `${disk.toFixed(1)}%`;

    setBar($("cpuBar"), cpu);
    setBar($("memBar"), mem);
    setBar($("diskBar"), disk);

    setStatusPill(data.status ?? "ok");
    renderAlerts(data.alerts ?? []);

    $("meta").textContent = `Host: ${data.hostname ?? "—"} • Uptime: ${data.uptime_seconds ?? "—"}s • Report: ${data.report_path ?? "—"}`;
  } catch (e) {
    $("statusPill").textContent = "Error";
    $("statusPill").style.color = "var(--bad)";
  }
}

$("refreshBtn").addEventListener("click", refresh);
refresh();
setInterval(refresh, 5000);


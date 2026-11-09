/* Aquarium Parameter Log — frontend logic */
const params = new URLSearchParams(location.search);
let currentTankId = params.get("tank") ? Number(params.get("tank")) : null;
let chart = null;

const $ = (sel) => document.querySelector(sel);

async function loadTanks() {
  const res = await fetch("/tanks");
  const tanks = await res.json();
  const list = $("#tank-list");
  list.innerHTML = "";
  if (tanks.length === 0) {
    list.innerHTML = '<li class="empty">No tanks yet — add one above.</li>';
    return;
  }
  for (const t of tanks) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `/?tank=${t.id}`;
    a.textContent = t.name;
    if (t.id === currentTankId) a.style.color = "var(--accent)";
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = t.water_type;
    li.append(a, badge);
    list.append(li);
  }
}

async function loadReadings() {
  if (!currentTankId) return;
  $("#readings").hidden = false;
  const res = await fetch(`/readings?tank_id=${currentTankId}`);
  const readings = await res.json();

  const tankEl = $(`#tank-list li[data-id="${currentTankId}"] a`);
  $("#reading-title").textContent = `Readings — ${tankEl ? tankEl.textContent : "Tank " + currentTankId}`;

  const rows = $("#reading-rows");
  rows.innerHTML = "";
  if (readings.length === 0) {
    rows.innerHTML = '<tr><td colspan="6" class="empty">No readings yet.</td></tr>';
  }
  for (const r of [...readings].reverse()) {
    const tr = document.createElement("tr");
    const cells = [
      new Date(r.measured_at).toLocaleString(),
      r.ph, r.temperature_c, r.nh3_ppm, r.no2_ppm, r.no3_ppm,
    ];
    for (const c of cells) {
      const td = document.createElement("td");
      td.textContent = c === null || c === undefined ? "—" : c;
      tr.append(td);
    }
    rows.append(tr);
  }
  drawChart(readings);
}

function drawChart(readings) {
  const ordered = [...readings].reverse();
  const labels = ordered.map((r) =>
    new Date(r.measured_at).toLocaleDateString()
  );
  const datasets = [
    ["pH", "ph", "#38bdf8"],
    ["Temp °C", "temperature_c", "#f87171"],
    ["NH3", "nh3_ppm", "#fbbf24"],
    ["NO2", "no2_ppm", "#a78bfa"],
    ["NO3", "no3_ppm", "#34d399"],
  ].map(([label, key, color]) => ({
    label,
    data: ordered.map((r) => r[key]),
    borderColor: color,
    backgroundColor: color,
    spanGaps: true,
    tension: 0.3,
  }));

  if (chart) chart.destroy();
  chart = new Chart($("#trend-chart"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
      },
    },
  });
}

$("#tank-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const payload = {
    name: form.name.value.trim(),
    water_type: form.water_type.value,
  };
  if (!payload.name) return;
  const res = await fetch("/tanks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.status === 201) {
    form.name.value = "";
    await loadTanks();
  }
});

$("#reading-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentTankId) {
    alert("Select a tank first.");
    return;
  }
  const form = e.target;
  const payload = { tank_id: currentTankId };
  for (const key of ["ph", "temperature_c", "nh3_ppm", "no2_ppm", "no3_ppm"]) {
    if (form[key].value !== "") payload[key] = Number(form[key].value);
  }
  const res = await fetch("/readings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.status === 201) {
    for (const key of ["ph", "temperature_c", "nh3_ppm", "no2_ppm", "no3_ppm"]) {
      form[key].value = "";
    }
    await loadReadings();
  } else {
    const err = await res.json();
    alert(err.detail || "Failed to save reading");
  }
});

loadTanks().then(loadReadings);

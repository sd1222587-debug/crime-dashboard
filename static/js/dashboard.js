async function loadData() {
  const res = await fetch("/api/summary");
  const data = await res.json();

  // Metric cards
  document.getElementById("totalCrimes").textContent = data.total.toLocaleString();
  document.getElementById("crimeTypes").textContent = data.by_type.length;
  document.getElementById("totalDistricts").textContent = data.by_district.length;

  const peakHour = data.by_hour.reduce((a, b) => a.count > b.count ? a : b);
  document.getElementById("peakHour").textContent = peakHour.hour + ":00";

  // Monthly trend chart
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const monthCounts = Array(12).fill(0);
  data.by_month.forEach(r => { monthCounts[r.month - 1] = r.count; });

  new Chart(document.getElementById("trendChart"), {
    type: "line",
    data: {
      labels: months,
      datasets: [{
        label: "Crimes",
        data: monthCounts,
        borderColor: "#3266ad",
        backgroundColor: "rgba(50,102,173,0.08)",
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true }
      }
    }
  });

  // Crime type doughnut chart
  const top6 = data.by_type.slice(0, 6);
  new Chart(document.getElementById("typeChart"), {
    type: "doughnut",
    data: {
      labels: top6.map(r => r.crime_type),
      datasets: [{
        data: top6.map(r => r.count),
        backgroundColor: ["#3266ad","#E24B4A","#EF9F27","#1D9E75","#7F77DD","#73726c"],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "55%",
      plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } }
    }
  });

  // District bar chart
  const top10dist = data.by_district.slice(0, 10);
  new Chart(document.getElementById("districtChart"), {
    type: "bar",
    data: {
      labels: top10dist.map(r => "District " + r.district),
      datasets: [{
        label: "Crimes",
        data: top10dist.map(r => r.count),
        backgroundColor: "#3266ad",
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { beginAtZero: true }
      }
    }
  });

  // Hour bar chart
  new Chart(document.getElementById("hourChart"), {
    type: "bar",
    data: {
      labels: data.by_hour.map(r => r.hour + ":00"),
      datasets: [{
        label: "Crimes",
        data: data.by_hour.map(r => r.count),
        backgroundColor: "#E24B4A",
        borderRadius: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 9 } } },
        y: { beginAtZero: true }
      }
    }
  });
}

async function predictRisk() {
  const crime_type = document.getElementById("crimeTypeInput").value;
  const district   = document.getElementById("districtInput").value;
  const hour       = document.getElementById("hourInput").value;

  const res = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ crime_type, district, hour: parseInt(hour) })
  });

  const data = await res.json();
  const box  = document.getElementById("riskResult");
  box.className = "risk-result risk-" + data.risk_level;
  box.textContent = "Risk Level: " + data.risk_level + " (" + data.confidence + "% confidence)";
}

loadData();
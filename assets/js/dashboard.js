// Global chart references
let charts = {};

// ── VIEW ROUTING ───────────────────────────────────
let dashboardInitialized = false;

function showHome() {
  const homePage = document.getElementById('home-page');
  const appContainer = document.querySelector('.app-container');
  if (!homePage || !appContainer) return;
  appContainer.classList.add('lp-hidden');
  homePage.classList.remove('lp-hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showDashboard(targetSection) {
  const homePage = document.getElementById('home-page');
  const appContainer = document.querySelector('.app-container');
  if (!homePage || !appContainer) return;
  homePage.classList.add('lp-hidden');
  appContainer.classList.remove('lp-hidden');
  window.scrollTo({ top: 0, behavior: 'instant' });
  // Navigate to a specific section if requested
  if (targetSection) {
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    const sections = document.querySelectorAll('.dashboard-section');
    const topbarName = document.getElementById('topbar-page-name');
    navItems.forEach(n => n.classList.remove('active'));
    sections.forEach(s => {
      s.classList.remove('active');
      if (s.id === targetSection) s.classList.add('active');
    });
    const matchingNav = document.querySelector(`.nav-item[data-section="${targetSection}"]`);
    if (matchingNav) matchingNav.classList.add('active');
    if (topbarName) topbarName.textContent = PAGE_NAMES[targetSection] || targetSection;
    // Lazy-load special sections
    if (targetSection === 'leaderboard') setTimeout(initLeaderboard, 60);
    if (targetSection === 'justification') setTimeout(loadJustificationReport, 60);
  }
  // Only fetch data once
  if (!dashboardInitialized) {
    dashboardInitialized = true;
    loadDashboardData();
  }
}

// Page name mapping for topbar
const PAGE_NAMES = {
  dashboard:      "Dashboard Overview",
  about:          "About the Dataset",
  objectives:     "Project Objectives & Workflow",
  implementation: "Source Code Viewer",
  results:        "Results & Visualizations",
  leaderboard:    "Player Efficiency Leaderboard",
  sdg:            "SDG Sustainability Impact"
};

document.addEventListener("DOMContentLoaded", () => {
  initNav();

  // Wire landing page CTA buttons
  const lpIds = [
    ['lp-hero-enter',      () => showDashboard('dashboard')],
    ['lp-hero-methodology',() => showDashboard('justification')],
    ['lp-footer-enter',    () => showDashboard('dashboard')],
  ];
  lpIds.forEach(([id, fn]) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', fn);
  });

  const runBtn = document.getElementById("run-pipeline-btn");
  if (runBtn) runBtn.addEventListener("click", runPipeline);

  // #12 — Dynamic footer year
  const yearEl = document.getElementById('lp-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // #13 — Back-to-top button visibility
  const backBtn = document.getElementById('back-to-top');
  if (backBtn) {
    window.addEventListener('scroll', () => {
      backBtn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    backBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // #15 — Mark live stat elements as loading
  document.querySelectorAll('.counter-val, .hud-value, .sdg-metric-val').forEach(el => {
    if (el.textContent.trim() === '—' || el.textContent.trim() === '−') {
      el.setAttribute('data-loading', 'true');
    }
  });

  // #16 — CSV Export button
  const csvBtn = document.getElementById('export-csv-btn');
  if (csvBtn) csvBtn.addEventListener('click', exportLeaderboardCSV);
});

// ── Sidebar Navigation ─────────────────────────────
function initNav() {
  const navItems   = document.querySelectorAll(".nav-item[data-section]");
  const sections   = document.querySelectorAll(".dashboard-section");
  const topbarName = document.getElementById("topbar-page-name");

  // Home button in sidebar
  const homeBtn = document.getElementById("nav-home-btn");
  if (homeBtn) {
    homeBtn.addEventListener("click", () => {
      // Deactivate all nav items
      navItems.forEach(n => n.classList.remove("active"));
      showHome();
    });
  }

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const target = item.getAttribute("data-section");

      // Update active nav
      navItems.forEach(n => n.classList.remove("active"));
      item.classList.add("active");

      // Show matching section
      sections.forEach(s => {
        s.classList.remove("active");
        if (s.id === target) s.classList.add("active");
      });

      // Update topbar
      if (topbarName) topbarName.textContent = PAGE_NAMES[target] || target;

      // #18 — Dynamic document title
      document.title = `${PAGE_NAMES[target] || target} — Howzat!`;

      // Lazy-init leaderboard on first visit
      if (target === "leaderboard") {
        setTimeout(initLeaderboard, 60);
      }
      // Lazy-load justification report on first visit
      if (target === "justification") {
        setTimeout(loadJustificationReport, 60);
      }

      // Ensure dashboard data is loaded when navigating inside app
      if (!dashboardInitialized) {
        dashboardInitialized = true;
        loadDashboardData();
      }
    });
  });

  // Code file tabs
  const codeTabs    = document.querySelectorAll(".code-tab-btn");
  const codeViewers = document.querySelectorAll(".code-viewer-content");

  codeTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-target");
      codeTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      codeViewers.forEach(v => {
        v.classList.remove("active");
        if (v.id === targetId) v.classList.add("active");
      });
    });
  });

  // Viz sub-tabs (Interactive / PNG / Table)
  const vizTabs  = document.querySelectorAll(".viz-tab-btn");
  const vizViews = document.querySelectorAll(".viz-view-content");

  vizTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-target");
      vizTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      vizViews.forEach(v => {
        v.classList.remove("active");
        if (v.id === targetId) v.classList.add("active");
      });
    });
  });
}

// Fetch and Render Dashboard Data
async function loadDashboardData() {
  try {
    // 1. Fetch data cleaning stats
    const cleanRes = await fetch("/api/cleaning-stats");
    const cleanStats = await cleanRes.json();
    updateCleaningStatsDOM(cleanStats);

    // 2. Fetch evaluation metrics & results
    const metricsRes = await fetch("/api/metrics");
    const metricsData = await metricsRes.json();
    updateMetricsDOM(metricsData);
    renderMetricsCharts(metricsData);

    // 3. Fetch SDG sustainability data
    const sdgRes = await fetch("/api/sdg-data");
    const sdgData = await sdgRes.json();
    updateSdgDOM(sdgData);
    renderSdgCharts(sdgData);

    // #15 — Remove loading skeleton once data is in
    document.querySelectorAll('[data-loading="true"]').forEach(el => {
      el.removeAttribute('data-loading');
    });

    // #6 — Update leaderboard badge dynamically
    if (cleanStats && cleanStats.active_players) {
      const badge = document.querySelector('#nav-leaderboard-badge');
      if (badge) badge.textContent = cleanStats.active_players.toLocaleString();
    }

  } catch (error) {
    console.error("Error loading dashboard data:", error);
  }
}

// Animate Counters
function animateCounter(id, endValue, isDecimal = false, suffix = "") {
  const element = document.getElementById(id);
  if (!element) return;
  
  let start = 0;
  const duration = 1500; // 1.5s animation
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Easing function (outQuad)
    const easeProgress = progress * (2 - progress);
    const currentValue = start + easeProgress * (endValue - start);
    
    if (isDecimal) {
      // 4 decimal places for efficiency/evaluation, 2 for percentage
      const decimals = id.includes("r2") || id.includes("rmse") || id.includes("mae") || id.includes("efficiency") ? 4 : 2;
      element.textContent = currentValue.toFixed(decimals) + suffix;
    } else {
      element.textContent = Math.floor(currentValue).toLocaleString() + suffix;
    }
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      if (isDecimal) {
        const decimals = id.includes("r2") || id.includes("rmse") || id.includes("mae") || id.includes("efficiency") ? 4 : 2;
        element.textContent = endValue.toFixed(decimals) + suffix;
      } else {
        element.textContent = endValue.toLocaleString() + suffix;
      }
    }
  }
  
  requestAnimationFrame(update);
}

// Update DOM for Data Cleaning Stats
function updateCleaningStatsDOM(data) {
  if (data.status === "error") return;

  const recBefore = document.getElementById("desc-records-before");
  if (recBefore) recBefore.textContent = data.before.toLocaleString();

  const recAfter = document.getElementById("desc-records-after");
  if (recAfter) recAfter.textContent = data.after.toLocaleString();

  const dups = document.getElementById("desc-duplicates");
  if (dups) dups.textContent = data.duplicates.toLocaleString();

  const outliers = document.getElementById("desc-outliers");
  if (outliers) outliers.textContent = data.outliers.toLocaleString();

  const imputed = document.getElementById("stat-imputed-val");
  if (imputed) imputed.textContent = data.imputed.toLocaleString();

  // Hero counters
  animateCounter("hero-pop-size", data.after);
  animateCounter("hero-sample-size", 150);

  // Sidebar quick stat
  const sbPop = document.getElementById("sb-pop");
  if (sbPop) sbPop.textContent = data.after.toLocaleString();
}

// Update DOM for Evaluation & Metrics
function updateMetricsDOM(data) {
  if (!data.verdict) return;

  const verdict = data.verdict;
  const table   = data.table;

  // Hero cards
  const samplingEl = document.getElementById("hero-best-sampling");
  if (samplingEl) samplingEl.textContent = verdict.best_sampling_method_by_avg_r2.replace("sample_", "").toUpperCase();

  const modelEl = document.getElementById("hero-best-model");
  if (modelEl) modelEl.textContent = verdict.best_overall_model.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  // Verdict panel
  const vModel = document.getElementById("verdict-best-model");
  if (vModel) vModel.textContent = verdict.best_overall_model.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  const vSampling = document.getElementById("verdict-best-sampling");
  if (vSampling) vSampling.textContent = verdict.best_sampling_method_by_avg_r2.replace("sample_", "").toUpperCase() + " SAMPLING";

  animateCounter("verdict-r2",   verdict.best_sample_r2,   true);
  animateCounter("verdict-rmse", verdict.best_sample_rmse, true);
  animateCounter("verdict-mae",  verdict.best_sample_mae,  true);

  // Sidebar quick stats
  const sbR2 = document.getElementById("sb-r2");
  if (sbR2) sbR2.textContent = verdict.best_overall_r2.toFixed(4);
  const sbSampling = document.getElementById("sb-sampling");
  if (sbSampling) sbSampling.textContent = verdict.best_sampling_method_by_avg_r2.replace("sample_", "").toUpperCase();

  // Metrics Table
  const tableBody = document.getElementById("metrics-table-body");
  if (tableBody) {
    tableBody.innerHTML = "";
    table.forEach(row => {
      const tr = document.createElement("tr");
      let badgeClass = "lr", modelShort = "Linear Regression";
      if (row.Model === "random_forest")  { badgeClass = "rf";  modelShort = "Random Forest"; }
      else if (row.Model === "xgboost")   { badgeClass = "xgb"; modelShort = "XGBoost"; }

      tr.innerHTML = `
        <td><span class="badge ${badgeClass}">${modelShort}</span></td>
        <td>${row.Sampling_Method.replace("sample_", "").replace("population", "Full Population").toUpperCase()}</td>
        <td class="font-mono" style="color:var(--accent-green)">${row.R2_Score.toFixed(6)}</td>
        <td class="font-mono">${row.MAE.toFixed(6)}</td>
        <td class="font-mono">${row.RMSE.toFixed(6)}</td>
      `;
      tableBody.appendChild(tr);
    });
  }
}

// Update DOM for SDG Sustainability
function updateSdgDOM(data) {
  animateCounter("hero-trees", data.total_trees);

  if (data.sampling_means && data.sampling_means.population) {
    animateCounter("hero-avg-efficiency", data.sampling_means.population.efficiency, true);
  }

  const totalTreesEl = document.getElementById("sdg-total-trees");
  if (totalTreesEl) totalTreesEl.textContent = data.total_trees.toLocaleString();

  const avgTreesEl = document.getElementById("sdg-avg-trees");
  if (avgTreesEl) avgTreesEl.textContent = Math.round(data.avg_trees_per_player).toLocaleString();

  const topBatsmanNameEl = document.getElementById("sdg-top-batsman-name");
  if (topBatsmanNameEl) topBatsmanNameEl.textContent = data.top_batsman.name;

  const topBatsmanTreesEl = document.getElementById("sdg-top-batsman-trees");
  if (topBatsmanTreesEl) topBatsmanTreesEl.textContent = data.top_batsman.trees.toLocaleString() + " Trees";

  // Sidebar quick stat
  const sbTrees = document.getElementById("sb-trees");
  if (sbTrees) sbTrees.textContent = (data.total_trees / 1000000).toFixed(2) + "M";

  // Team Rankings
  const rankingBody = document.getElementById("sdg-ranking-body");
  if (rankingBody) {
    rankingBody.innerHTML = "";
    data.team_rankings.forEach((team, index) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="rank-num">#${index + 1}</span></td>
        <td style="font-weight: 600; color: var(--text-primary)">${team.Team}</td>
        <td class="font-mono">${team.Dot_Balls.toLocaleString()}</td>
        <td class="font-mono" style="color: var(--accent-green); font-weight: 700">${team.Trees_Planted.toLocaleString()}</td>
      `;
      rankingBody.appendChild(tr);
    });
  }
}

// Chart.js Helper to generate Neon Gradients and Shadow Options
function getNeonLineOptions(color) {
  return {
    borderColor: color,
    borderWidth: 2,
    pointBackgroundColor: color,
    pointBorderColor: "#fff",
    pointHoverBackgroundColor: "#fff",
    pointHoverBorderColor: color,
    pointRadius: 4,
    pointHoverRadius: 6,
    tension: 0.2
  };
}

// Destroy existing chart if it exists
function destroyChart(name) {
  if (charts[name]) {
    charts[name].destroy();
  }
}

// Render Model Metrics Chart.js
function renderMetricsCharts(data) {
  const table = data.table;
  const summary = data.sampling_summary;
  
  // Chart 8: Model Accuracy Comparison (Average R2 by model type)
  destroyChart("modelAccuracy");
  const models = ["linear_regression", "random_forest", "xgboost"];
  const avgR2ByModel = models.map(m => {
    const subset = table.filter(r => r.Model === m);
    const sum = subset.reduce((acc, curr) => acc + curr.R2_Score, 0);
    return sum / subset.length;
  });
  
  const ctx8 = document.getElementById("chart-model-accuracy").getContext("2d");
  charts["modelAccuracy"] = new Chart(ctx8, {
    type: "bar",
    data: {
      labels: ["Linear Regression", "Random Forest", "XGBoost"],
      datasets: [{
        label: "Mean R² Score",
        data: avgR2ByModel,
        backgroundColor: ["#00ccff", "#ff5500", "#00ff66"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0.90,
          max: 1.0,
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // Chart 9: R2 Comparison Across Sampling Methods
  destroyChart("r2Comparison");
  
  // Formulate data
  const methods = ["population", "sample_random", "sample_systematic", "sample_stratified", "sample_cluster"];
  const labels = ["Full Pop", "Random", "Systematic", "Stratified", "Cluster"];
  
  const lrR2 = methods.map(m => table.find(r => r.Model === "linear_regression" && r.Sampling_Method === m)?.R2_Score || 0);
  const rfR2 = methods.map(m => table.find(r => r.Model === "random_forest" && r.Sampling_Method === m)?.R2_Score || 0);
  const xgbR2 = methods.map(m => table.find(r => r.Model === "xgboost" && r.Sampling_Method === m)?.R2_Score || 0);
  
  const ctx9 = document.getElementById("chart-r2-comparison").getContext("2d");
  charts["r2Comparison"] = new Chart(ctx9, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Linear Regression", data: lrR2, backgroundColor: "#00ccff", borderRadius: 4 },
        { label: "Random Forest", data: rfR2, backgroundColor: "#ff5500", borderRadius: 4 },
        { label: "XGBoost", data: xgbR2, backgroundColor: "#00ff66", borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0.90,
          max: 1.002,
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { labels: { color: "#ffffff" } }
      }
    }
  });

  // Chart 10: RMSE Comparison
  destroyChart("rmseComparison");
  const lrRmse = methods.map(m => table.find(r => r.Model === "linear_regression" && r.Sampling_Method === m)?.RMSE || 0);
  const rfRmse = methods.map(m => table.find(r => r.Model === "random_forest" && r.Sampling_Method === m)?.RMSE || 0);
  const xgbRmse = methods.map(m => table.find(r => r.Model === "xgboost" && r.Sampling_Method === m)?.RMSE || 0);

  const ctx10 = document.getElementById("chart-rmse-comparison").getContext("2d");
  charts["rmseComparison"] = new Chart(ctx10, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Linear Regression", data: lrRmse, backgroundColor: "#00ccff", borderRadius: 4 },
        { label: "Random Forest", data: rfRmse, backgroundColor: "#ff5500", borderRadius: 4 },
        { label: "XGBoost", data: xgbRmse, backgroundColor: "#00ff66", borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { labels: { color: "#ffffff" } }
      }
    }
  });

  // Chart 11: MAE Comparison
  destroyChart("maeComparison");
  const lrMae = methods.map(m => table.find(r => r.Model === "linear_regression" && r.Sampling_Method === m)?.MAE || 0);
  const rfMae = methods.map(m => table.find(r => r.Model === "random_forest" && r.Sampling_Method === m)?.MAE || 0);
  const xgbMae = methods.map(m => table.find(r => r.Model === "xgboost" && r.Sampling_Method === m)?.MAE || 0);

  const ctx11 = document.getElementById("chart-mae-comparison").getContext("2d");
  charts["maeComparison"] = new Chart(ctx11, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        { label: "Linear Regression", data: lrMae, backgroundColor: "#00ccff", borderRadius: 4 },
        { label: "Random Forest", data: rfMae, backgroundColor: "#ff5500", borderRadius: 4 },
        { label: "XGBoost", data: xgbMae, backgroundColor: "#00ff66", borderRadius: 4 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { labels: { color: "#ffffff" } }
      }
    }
  });
}

// Render SDG Sustainability charts
function renderSdgCharts(data) {
  // Chart 5: Trees Planted by Top Batsmen
  destroyChart("topBatsmenTrees");
  const batsmanNames = data.top_batsmen_list.map(b => b.name);
  const batsmanTrees = data.top_batsmen_list.map(b => b.trees);
  
  const ctx5 = document.getElementById("chart-top-batsmen-trees").getContext("2d");
  charts["topBatsmenTrees"] = new Chart(ctx5, {
    type: "bar",
    data: {
      labels: batsmanNames,
      datasets: [{
        label: "Trees Planted (Dot Balls × 19)",
        data: batsmanTrees,
        backgroundColor: "rgba(0, 255, 102, 0.75)",
        borderColor: "#00ff66",
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // Chart 6 & 7: Mean Trees and Mean Efficiency
  destroyChart("meanTrees");
  const samplingLabels = ["Population", "Random", "Systematic", "Stratified", "Cluster"];
  const meanTreesData = [
    data.sampling_means.population.trees,
    data.sampling_means.sample_random.trees,
    data.sampling_means.sample_systematic.trees,
    data.sampling_means.sample_stratified.trees,
    data.sampling_means.sample_cluster.trees
  ];

  const ctx6 = document.getElementById("chart-mean-trees").getContext("2d");
  charts["meanTrees"] = new Chart(ctx6, {
    type: "bar",
    data: {
      labels: samplingLabels,
      datasets: [{
        label: "Mean Trees per Batsman-Season",
        data: meanTreesData,
        backgroundColor: ["#ff5500", "#00ff66", "#00ff66", "#00ff66", "#00ff66"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  destroyChart("meanEfficiency");
  const meanEffData = [
    data.sampling_means.population.efficiency,
    data.sampling_means.sample_random.efficiency,
    data.sampling_means.sample_systematic.efficiency,
    data.sampling_means.sample_stratified.efficiency,
    data.sampling_means.sample_cluster.efficiency
  ];

  const ctx7 = document.getElementById("chart-mean-efficiency").getContext("2d");
  charts["meanEfficiency"] = new Chart(ctx7, {
    type: "bar",
    data: {
      labels: samplingLabels,
      datasets: [{
        label: "Mean Efficiency Score",
        data: meanEffData,
        backgroundColor: ["#00ccff", "#00ff66", "#00ff66", "#00ff66", "#00ff66"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          grid: { color: "#22222b" },
          ticks: { color: "#8e8e9f" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#8e8e9f" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Trigger Pipeline execution dynamically from browser UI
async function runPipeline() {
  const overlay = document.getElementById("pipeline-overlay");
  const logDiv = document.getElementById("pipeline-logs-content");

  if (!overlay || !logDiv) return;

  overlay.classList.add("active");
  logDiv.innerHTML = "> Starting Howzat! full sports analytics & sustainability pipeline...\n";

  // #4 — 30-second timeout guard
  let pipelineTimedOut = false;
  const timeoutId = setTimeout(() => {
    pipelineTimedOut = true;
    logDiv.innerHTML += "\n[TIMEOUT] Pipeline did not respond within 30 seconds.\n> Is the Flask server running? Check your terminal.\n";
    const closeBtn = document.createElement("button");
    closeBtn.className = "cta-button";
    closeBtn.style.cssText = "margin-top:1rem";
    closeBtn.textContent = "Dismiss";
    closeBtn.onclick = () => { overlay.classList.remove("active"); closeBtn.remove(); };
    overlay.appendChild(closeBtn);
  }, 30000);

  try {
    const res = await fetch("/api/run-pipeline", { method: "POST" });
    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    while (true) {
      if (pipelineTimedOut) break;
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      logDiv.innerHTML += chunk;
      logDiv.scrollTop = logDiv.scrollHeight;
    }

    clearTimeout(timeoutId);
    if (!pipelineTimedOut) {
      logDiv.innerHTML += "\n> Howzat! Pipeline completed successfully. Re-loading dashboard...\n";
      await loadDashboardData();
      setTimeout(() => { overlay.classList.remove("active"); }, 3000);
    }

  } catch (error) {
    clearTimeout(timeoutId);
    logDiv.innerHTML += `\n[ERROR] Pipeline run failed: ${error.message}\n> Check that the Flask server is running on port 5001.\n`;
    console.error("Pipeline failure:", error);
    const closeBtn = document.createElement("button");
    closeBtn.className = "cta-button";
    closeBtn.style.marginTop = "1rem";
    closeBtn.textContent = "Dismiss";
    closeBtn.onclick = () => { overlay.classList.remove("active"); closeBtn.remove(); };
    overlay.appendChild(closeBtn);
  }
}

// ============================================================
// LEADERBOARD MODULE
// ============================================================
let leaderboardDebounceTimer = null;

async function loadLeaderboard() {
  const search = document.getElementById("player-search-input")?.value || "";
  const team   = document.getElementById("team-filter-select")?.value || "";
  const limit  = document.getElementById("limit-select")?.value || "20";

  const params = new URLSearchParams({ limit, search, team });

  try {
    const res = await fetch(`/api/top-players?${params.toString()}`);
    const data = await res.json();

    if (data.status !== "success") return;

    // Populate team dropdown (only on first load)
    const teamSelect = document.getElementById("team-filter-select");
    if (teamSelect && teamSelect.options.length === 1 && data.teams) {
      data.teams.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = t;
        teamSelect.appendChild(opt);
      });
    }

    // Update count badge
    const countEl = document.getElementById("leaderboard-count");
    if (countEl) countEl.textContent = `${data.players.length} of ${data.total_population} players`;

    // Render table
    const tbody = document.getElementById("leaderboard-tbody");
    if (!tbody) return;

    if (data.players.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 2rem; color: var(--text-muted)">No players found.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    const maxEff = data.players.reduce((m, p) => Math.max(m, p.efficiency_score), 0);

    data.players.forEach((player, idx) => {
      const rank = idx + 1;
      let rankClass = "";
      if (rank === 1) rankClass = "gold";
      else if (rank === 2) rankClass = "silver";
      else if (rank === 3) rankClass = "bronze";

      const effPct = maxEff > 0 ? (player.efficiency_score / maxEff * 100).toFixed(1) : 0;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="rank-badge ${rankClass}">${rank}</span></td>
        <td style="font-weight: 600; color: var(--text-primary)">${player.name}</td>
        <td style="font-size: 0.8rem; color: var(--text-muted)">${player.team}</td>
        <td class="font-mono">${player.matches}</td>
        <td class="font-mono" style="font-weight: 600">${player.runs.toLocaleString()}</td>
        <td class="font-mono">${player.strike_rate.toFixed(1)}</td>
        <td class="font-mono">${player.batting_average.toFixed(1)}</td>
        <td class="font-mono">${player.dot_balls.toLocaleString()}</td>
        <td class="font-mono" style="color: var(--neon-green); font-weight: 600">${player.trees_planted.toLocaleString()}</td>
        <td>
          <div class="eff-bar-wrapper">
            <div class="eff-bar"><div class="eff-bar-fill" style="width: ${effPct}%"></div></div>
            <span class="font-mono" style="color: var(--neon-orange); font-weight: 700; font-size: 0.85rem">${player.efficiency_score.toFixed(2)}</span>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (e) {
    console.error("Error loading leaderboard:", e);
  }
}

function initLeaderboard() {
  loadLeaderboard();

  const searchInput = document.getElementById("player-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(leaderboardDebounceTimer);
      leaderboardDebounceTimer = setTimeout(loadLeaderboard, 350);
    });
  }

  const teamSelect = document.getElementById("team-filter-select");
  if (teamSelect) teamSelect.addEventListener("change", loadLeaderboard);

  const limitSelect = document.getElementById("limit-select");
  if (limitSelect) limitSelect.addEventListener("change", loadLeaderboard);
}



// ============================================================
// JUSTIFICATION REPORT MODULE
// ============================================================
let justificationLoaded = false;

async function loadJustificationReport() {
  if (justificationLoaded) return;
  const container = document.getElementById("justification-content");
  if (!container) return;

  try {
    const res = await fetch("/api/justification");
    const md  = await res.text();

    // Lightweight markdown → HTML renderer (tables, headings, code, bold, italic)
    let html = md
      // Escape HTML entities first
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

      // H1
      .replace(/^# (.+)$/gm, '<h1 style="font-size:1.6rem;font-weight:900;color:var(--text-primary);letter-spacing:-0.5px;margin:0 0 0.5rem">$1</h1>')
      // H2
      .replace(/^## (.+)$/gm, '<h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary);margin:2rem 0 0.75rem;border-bottom:1px solid var(--border);padding-bottom:0.4rem">$1</h2>')
      // H3
      .replace(/^### (.+)$/gm, '<h3 style="font-size:1rem;font-weight:700;color:var(--accent-orange);margin:1.5rem 0 0.5rem">$1</h3>')
      // H4
      .replace(/^#### (.+)$/gm, '<h4 style="font-size:0.9rem;font-weight:700;color:var(--accent-blue);margin:1rem 0 0.35rem">$1</h4>')

      // Bold + italic
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--text-primary)">$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')

      // Inline code
      .replace(/`([^`]+)`/g, '<code style="font-family:var(--font-mono);font-size:0.82em;background:rgba(255,255,255,0.06);border-radius:4px;padding:0.1em 0.4em;color:var(--accent-green)">$1</code>')

      // Horizontal rule
      .replace(/^---+$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:1.5rem 0">')

      // Blockquote
      .replace(/^&gt; \*\*(.+?)\*\*(.*)$/gm, '<blockquote style="border-left:3px solid var(--accent-orange);padding:0.75rem 1rem;background:rgba(255,85,0,0.05);border-radius:0 8px 8px 0;margin:1rem 0"><strong style="color:var(--text-primary)">$1</strong>$2</blockquote>')
      .replace(/^&gt; (.+)$/gm, '<blockquote style="border-left:3px solid var(--accent-orange);padding:0.75rem 1rem;background:rgba(255,85,0,0.05);border-radius:0 8px 8px 0;margin:1rem 0">$1</blockquote>')

      // Table header separator line (skip)
      .replace(/^\|[-| :]+\|$/gm, '__TABLE_SEP__')

      // Tables
      .replace(/(\|.+\|\n__TABLE_SEP__\n(?:\|.+\|\n?)+)/g, (match) => {
        const lines = match.split('\n').filter(l => l.trim() && !l.includes('__TABLE_SEP__'));
        if (lines.length < 2) return match;
        const headers = lines[0].split('|').filter(c => c.trim()).map(c =>
          `<th style="background:rgba(10,10,16,0.9);color:var(--text-secondary);font-weight:600;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;padding:0.7rem 0.85rem;border-bottom:1px solid var(--border)">${c.trim()}</th>`
        );
        const rows = lines.slice(1).map(line => {
          const cells = line.split('|').filter(c => c.trim() !== undefined && line.includes('|')).slice(1,-1);
          return '<tr>' + cells.map(c =>
            `<td style="padding:0.7rem 0.85rem;border-bottom:1px solid var(--border);color:var(--text-secondary);font-size:0.85rem">${c.trim()}</td>`
          ).join('') + '</tr>';
        }).filter(r => r !== '<tr></tr>');
        return `<div class="table-wrapper" style="margin:1rem 0"><table><thead><tr>${headers.join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
      })

      .replace(/__TABLE_SEP__/g, '')

      // Ordered list items
      .replace(/^\d+\. (.+)$/gm, '<li style="margin:0.3rem 0;color:var(--text-secondary);line-height:1.6">$1</li>')
      // Unordered list items
      .replace(/^[-*] (.+)$/gm, '<li style="margin:0.3rem 0;color:var(--text-secondary);line-height:1.6">$1</li>')

      // Line breaks → paragraphs
      .replace(/\n\n/g, '</p><p style="font-size:0.9rem;line-height:1.7;color:var(--text-secondary);margin-bottom:0.75rem">')

      // Meta info lines (bold-colon pairs like **Project:** ...)
      .replace(/^(\*\*[A-Za-z ]+:\*\*)/gm, '<strong style="color:var(--text-muted)">$1</strong>');

    // Wrap in a container
    container.innerHTML = `
      <div style="padding:0.5rem 0.5rem 2rem">
        <p style="font-size:0.9rem;line-height:1.7;color:var(--text-secondary);margin-bottom:0.75rem">
          ${html}
        </p>
      </div>`;

    justificationLoaded = true;

  } catch (e) {
    container.innerHTML = `<div style="color:var(--accent-orange);padding:2rem">Error loading report: ${e.message}</div>`;
  }
}

// ── #16 CSV Export ──────────────────────────────────
function exportLeaderboardCSV() {
  const table = document.querySelector('#leaderboard-body')?.closest('table');
  if (!table) { alert('Load the leaderboard first.'); return; }

  const rows = [];
  const headers = [...table.querySelectorAll('thead th')].map(th => th.textContent.trim());
  rows.push(headers.join(','));

  table.querySelectorAll('tbody tr').forEach(tr => {
    const cells = [...tr.querySelectorAll('td')].map(td => {
      const text = td.textContent.trim().replace(/,/g, '');
      return `"${text}"`;
    });
    rows.push(cells.join(','));
  });

  const csv = rows.join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'ipl_leaderboard.csv';
  a.click();
  URL.revokeObjectURL(url);
}

// ── #17 Prism.js Syntax Highlighting ───────────────
function loadPrism() {
  if (window.Prism) { Prism.highlightAll(); return; }
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css';
  document.head.appendChild(link);

  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js';
  script.onload = () => {
    const pyScript = document.createElement('script');
    pyScript.src = 'https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js';
    pyScript.onload = () => {
      // Re-apply class so Prism picks up the code blocks
      document.querySelectorAll('pre code').forEach(block => {
        if (!block.classList.contains('language-python')) {
          block.classList.add('language-python');
        }
      });
      Prism.highlightAll();
    };
    document.head.appendChild(pyScript);
  };
  document.head.appendChild(script);
}

// Trigger Prism when Source Code section is visited
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-item[data-section="implementation"]').forEach(btn => {
    btn.addEventListener('click', () => setTimeout(loadPrism, 300));
  });
});
